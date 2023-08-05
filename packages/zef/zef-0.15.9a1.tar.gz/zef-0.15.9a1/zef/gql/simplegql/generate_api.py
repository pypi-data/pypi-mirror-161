# Copyright 2022 Synchronous Technologies Pte Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Assuming this file is not imported during zefdb init.
from ... import *
from ...ops import *
from functools import partial as P
from ...core.logger import log
import functools

from ariadne import ObjectType, QueryType, MutationType, EnumType, ScalarType

##############################
# * Utils
#----------------------------

@func
def is_core_scalar(z):
    return (
        is_a(z, AET.String) or
        is_a(z, AET.Int) or
        is_a(z, AET.Float) or
        is_a(z, AET.Bool)
    )
    
assert_type = Assert[is_a[ET.GQL_Type | ET.GQL_Enum | AET]][lambda z: f"{z} is not a GQL type"]
assert_field = Assert[is_a[RT.GQL_Field]][lambda z: f"{z} is not a GQL field"]

optional = single_or[None]

@func
def OutO(z, rt):
    if z is None:
        return None
    return z | Outs[rt] | optional | collect

@func
def fvalue(z, rt, *args):
    if len(args) == 0:
        return z | Out[rt] | value | collect
    else:
        default, = args
        return z | OutO[rt] | value_or[default] | collect

        
op_is_scalar = assert_type | is_a[AET | ET.GQL_Enum]
op_is_orderable = assert_type | is_a[AET.Float | AET.Int | AET.Time]
op_is_summable = assert_type | is_a[AET.Float | AET.Int]
op_is_stringlike = assert_type | is_a[AET.String]
op_is_list = assert_field | fvalue[RT.List][False] | collect
op_is_required = assert_field | fvalue[RT.Required][False] | collect
op_is_unique = assert_field | fvalue[RT.Unique][False] | collect
op_is_searchable = assert_field | fvalue[RT.Search][False] | collect
op_is_aggregable = assert_field | And[Not[op_is_list]][target | Or[op_is_orderable][op_is_summable]]
op_is_incoming = assert_field | fvalue[RT.Incoming][False] | collect

op_is_upfetch = assert_field | fvalue[RT.Upfetch][False] | collect
op_upfetch_field = (assert_type | out_rels[RT.GQL_Field]
                    | filter[op_is_upfetch]
                    | optional
                    | collect)
op_has_upfetch = op_upfetch_field | Not[equals[None]] | collect

########################################
# * Generating it all
#--------------------------------------

def generate_resolvers_fcts(schema_root):
    Query = QueryType()
    Mutation = MutationType()

    all_objects = [Query, Mutation]
    query_fields = []
    mutation_fields = []
    type_schemas = []
    enum_schemas = []

    extra_filters = {}


    TimeScalar = ScalarType("DateTime")
    all_objects += [TimeScalar]
    import datetime
    TimeScalar.set_serializer(lambda t: datetime.datetime.fromtimestamp(t.seconds_since_1970).isoformat())
    TimeScalar.set_value_parser(Time)

    for z_type in schema_root | Outs[RT.GQL_Type]:
        name = z_type | F.Name | collect
        Type = ObjectType(name)
        all_objects += [Type]

        field_schemas = []
        ref_field_schemas = []
        add_field_schemas = []
        upfetch_field_schemas = []
        aggregate_outs = []

        for z_field in z_type | out_rels[RT.GQL_Field]:
            field_name = z_field | F.Name | collect
            Type.set_field(field_name,
                            P(resolve_field, z_field=z_field))

            is_scalar = z_field | target | op_is_scalar | collect
            is_required = z_field | op_is_required | collect
            is_list = z_field | op_is_list | collect
            is_orderable = z_field | target | op_is_orderable | collect
            is_summable = z_field | target | op_is_orderable | collect
            is_aggregable = z_field | op_is_aggregable | collect

            if op_is_unique(z_field):
                assert is_scalar, "Unique fields must be scalars"
                assert not is_list, "Unique fields can't be lists"

            if op_is_upfetch(z_field):
                assert op_is_unique(z_field), "Upfetch field must be unique"
                assert is_required, "Upfetch field must be required"

            base_field_type = z_field | target | F.Name | collect
            if is_scalar:
                base_ref_field_type = base_field_type
            else:
                base_ref_field_type = base_field_type + "Ref" 

            if is_required:
                maybe_required = "!"
            else:
                maybe_required = ""
            if is_list:
                maybe_params = "(" + schema_generate_list_params(target(z_field), extra_filters) + ")"
                ref_field_type = "[" + base_ref_field_type + "]"
                # add_field_type = "[" + base_ref_field_type + maybe_required + "]"
                add_field_type = ref_field_type
                upfetch_field_type = "[" + base_ref_field_type + maybe_required + "]"
                field_type = "[" + base_field_type + maybe_required + "]"
            else:
                maybe_params = ""
                ref_field_type = base_ref_field_type
                # add_field_type = base_ref_field_type + maybe_required
                add_field_type = ref_field_type
                upfetch_field_type = base_ref_field_type + maybe_required
                field_type = base_field_type + maybe_required
            field_schemas += [f"{field_name}{maybe_params}: {field_type}"]
            add_field_schemas += [f"{field_name}: {add_field_type}"]
            ref_field_schemas += [f"{field_name}: {ref_field_type}"]
            upfetch_field_schemas += [f"{field_name}: {upfetch_field_type}"]

            if is_aggregable:
                if is_orderable:
                    aggregate_outs += [
                        f"{field_name}Min: {ref_field_type}",
                        f"{field_name}Max: {ref_field_type}",
                    ]
                if is_summable:
                    aggregate_outs += [f"{field_name}Sum: {ref_field_type}"]
                    aggregate_outs += [f"{field_name}Avg: {ref_field_type}"]

        field_schemas += ["id: ID!"]
        add_field_schemas += ["id: ID"]
        ref_field_schemas += ["id: ID"]
        # Note: upfetch does not get an id field
        Type.set_field("id", resolve_id)

        # Add the 3 top-level queries
        Query.set_field(f"get{name}",
                        P(resolve_get, type_node=z_type))
        Query.set_field(f"query{name}",
                        P(resolve_query, type_node=z_type))
        Query.set_field(f"aggregate{name}",
                        P(resolve_aggregate, type_node=z_type))
        # Add the 3 top-level mutations
        Mutation.set_field(f"add{name}",
                            P(resolve_add, type_node=z_type))
        Mutation.set_field(f"update{name}",
                            P(resolve_update, type_node=z_type))
        Mutation.set_field(f"delete{name}",
                            P(resolve_delete, type_node=z_type))
        has_upfetch = op_has_upfetch(z_type)
        if has_upfetch:
            Mutation.set_field(f"upfetch{name}",
                               P(resolve_upfetch, type_node=z_type))

        MutateResponse = ObjectType(f"Mutate{name}Response")
        all_objects += [MutateResponse]

        # MutateResponse.set_field(f"count", lambda x,*args,**kwds: x["count"])
        MutateResponse.set_field(to_camel_case(name), P(resolve_filter_response, type_node=z_type))

        query_params = schema_generate_list_params(z_type, extra_filters)
        field_schemas = '\n\t'.join(field_schemas)
        ref_field_schemas = '\n\t'.join(ref_field_schemas)
        add_field_schemas = '\n\t'.join(add_field_schemas)
        upfetch_field_schemas = '\n\t'.join(upfetch_field_schemas)
        aggregate_outs = '\n\t'.join(aggregate_outs)

        type_schemas += [f"""type {name} {{
        {field_schemas}
}}

input {name}Ref {{
        {ref_field_schemas}
}}

input Add{name}Input {{
        {add_field_schemas}
}}
        
input Update{name}Input {{
        filter: {name}Filter!
        set: {name}Ref
        remove: {name}Ref
}}

type Mutate{name}Response {{
        {to_camel_case(name)}({query_params}): [{name}]
        count: Int
}}

type Aggregate{name}Response {{
        count: Int
        {aggregate_outs}
}}

"""]
        if has_upfetch:
            type_schemas += [f"""
input Upfetch{name}Input {{
        {upfetch_field_schemas}
}}
"""]

        # id_fields = z_type > L[RT.GQL_Field] | filter[Z >> O[RT.IsID] | value_or[False]]

        # get_params = id_fields | map[lambda z: f"{value(z >> RT.Name)}: {value(z | target >> RT.Name)}"] | collect
        # get_params = ", ".join(get_params)
        get_params = "id: ID!"
        query_fields += [
            f"get{name}({get_params}): {name}",
            f"query{name}({query_params}): [{name}]",
            f"aggregate{name}({query_params}): Aggregate{name}Response",
        ]
        mutation_fields += [
            f"add{name}(input: [Add{name}Input!]!, upsert: Boolean): Mutate{name}Response",
            f"update{name}(input: Update{name}Input!): Mutate{name}Response",
            f"delete{name}(filter: {name}Filter!): Mutate{name}Response",
        ]
        if has_upfetch:
            mutation_fields += [
                f"upfetch{name}(input: [Upfetch{name}Input!]!): Mutate{name}Response",
            ]

    for z_enum in schema_root | Outs[RT.GQL_Enum]:
        name = z_enum | F.Name | collect

        opts = {}
        for z_opt in z_enum | Outs[RT.GQL_Field]:
            assert is_a(z_opt, AET.Enum(name))
            opt_en = value(z_opt)
            opts[opt_en.enum_value] = opt_en

        Enum = EnumType(name, opts)

        opt_list = '\n\t'.join(opts.keys())

        enum_schemas += [f"""enum {name} {{
\t{opt_list}
}}"""]

        all_objects += [Enum]

    # Always generate the Int scalar type 
    int_type = schema_root | Outs[RT.GQL_CoreScalarType][AET.Int] | single | collect
    if rae_type(int_type) not in [rae_type(x) for x in extra_filters.keys()]:
        extra_filters[int_type] = schema_generate_scalar_filter(int_type)

    query_fields = '\n\t'.join(query_fields)
    mutation_fields = '\n\t'.join(mutation_fields)
    type_schemas = '\n\n'.join(type_schemas)
    enum_schemas = '\n\n'.join(enum_schemas)
    extra_filters = '\n\n'.join(x["schema"] for x in extra_filters.values())
    schema = f"""
{type_schemas}

{enum_schemas}

type Query {{
\t{query_fields}
}}

type Mutation {{
    {mutation_fields}
}}
    
scalar DateTime
    
{extra_filters}
    
"""

    return schema, all_objects

################################################
# * Schema specific parts
#----------------------------------------------

def schema_generate_type_dispatch(z_type, extra_filters):
    if z_type not in extra_filters:
        extra_filters[z_type] = None
        if op_is_scalar(z_type):
            extra_filters[z_type] = schema_generate_scalar_filter(z_type)
        else:
            extra_filters[z_type] = schema_generate_type_filter(z_type, extra_filters)

def schema_generate_list_params(z_type, extra_filters):
    name = z_type | F.Name | collect
    schema_generate_type_dispatch(z_type, extra_filters)

    query_params = [
        f"filter: {name}Filter",
        # We probably want to change these to be proper cursors.
        "first: Int",
        "offset: Int",
    ]
    if extra_filters[z_type]["orderable"]:
        query_params += [f"order: {name}Order"]

    query_params = ", ".join(query_params)
    return query_params

def schema_generate_type_filter(z_type, extra_filters):
    name = z_type | F.Name | collect
    fil_name = f"{name}Filter"
    list_fil_name = f"{name}FilterList"
    order_name = f"{name}Order"
    orderable_name = f"{name}Orderable"

    fields = [
        # TODO: I Think this is if the field is present?
        # "has: [{fil_name}]",
        f"and: [{fil_name}]",
        f"or: [{fil_name}]",
        f"not: {fil_name}",
    ]

    orderable_fields = []

    # Every type has an ID field, which is slightly custom - functions as an
    # automatically generated "in"
    fields += [f"id: [ID!]"]

    for field in z_type | out_rels[RT.GQL_Field] | filter[op_is_searchable]:
        field_name = field | F.Name | collect
        field_type = target(field)
        field_type_name = field_type | F.Name | collect
        if is_a(field_type, AET.Bool):
            filter_name = Boolean
        else:
            filter_name = f"{field_type_name}Filter"
            schema_generate_type_dispatch(field_type, extra_filters)

        if op_is_list(field):
            fields += [f"{field_name}: {filter_name}List"]
        else:
            fields += [f"{field_name}: {filter_name}"]

    for field in z_type | out_rels[RT.GQL_Field] | filter[target | op_is_orderable]:
        orderable_fields += [field | F.Name | collect]

    fields = "\n\t".join(fields)
    orderable_fields = "\n\t".join(orderable_fields)

    out = f"""input {fil_name} {{
\t{fields}
}}
"""
    if len(orderable_fields) > 0:
        out += f"""
input {order_name} {{
        asc: {orderable_name}
        desc: {orderable_name}
        then: {order_name}
}}
        
input {list_fil_name} {{
\tany: {fil_name}
\tall: {fil_name}
\tsize: IntFilter
}}
    
enum {orderable_name} {{
\t{orderable_fields}
}}
"""
    return {"schema": out,
            "orderable": len(orderable_fields) > 0}
        

def schema_generate_scalar_filter(z_node):
    type_name = z_node | F.Name | collect
    fil_name = f"{type_name}Filter"
    list_fil_name = f"{type_name}FilterList"

    if is_a(z_node, AET.Bool):
        # Shoudln't need to do anything here, as it is true/false.
        return

    schema = f"""input {fil_name} {{
\teq: {type_name}
\tin: [{type_name}]
"""

    if op_is_orderable(z_node):
        schema += f"""\tle: {type_name}
\tlt: {type_name}
\tge: {type_name}
\tgt: {type_name}
\tbetween: {type_name}Range
"""

    if op_is_stringlike(z_node):
        schema += f"""\tcontains: String
"""

    schema += f"""}}

input {list_fil_name} {{
\tany: {fil_name}
\tall: {fil_name}
\tsize: IntFilter
}}
"""
    
    if op_is_orderable(z_node):
        schema += f"""\ninput {type_name}Range {{
\tmin: {type_name}!
\tmax: {type_name}!
}}"""

    return {"schema": schema,
            "orderable": op_is_orderable(z_node)}

####################################
# * Query resolvers
#----------------------------------

class ExternalError(Exception):
    pass

def resolve_get(_, info, *, type_node, **params):
    # Look for something that fits exactly what has been given in the params, assuming
    # that ariadne has done its work and validated the query.
    return find_existing_entity_by_id(info, type_node, params["id"])

def resolve_query(_, info, *, type_node, **params):
    ents = obtain_initial_list(type_node, params.get("filter", None), info)

    ents = handle_list_params(ents, type_node, params, info)

    return ents | collect

def resolve_aggregate(_, info, *, type_node, **params):
    # We can potentially defer the aggregation till later, by returning a kind
    # of lazy object here. However, for simplicity in the beginning, I will
    # aggregate everything, even if the query is only for a single field.

    ents = resolve_query(_, info, type_node=type_node, filter=params.get("filter", None))

    out = {"count": len(ents)}
    for z_field in type_node > L[RT.GQL_Field] | filter[op_is_aggregable]:
        vals = ents | map[lambda z: resolve_field(z, info, z_field=z_field)] | filter[Not[equals[None]]] | collect

        field_name = z_field | F.Name | collect

        if op_is_orderable(z_field | target):
            if len(vals) == 0:
                val_min = val_max = None
            else:
                val_min = min(vals)
                val_max = max(vals)

            # if isinstance(val_min, Time):
            #     val_min = str(val_min)
            #     val_max = str(val_max)

            out[f"{field_name}Min"] = val_min
            out[f"{field_name}Max"] = val_max

        if op_is_summable(z_field | target):
            if len(vals) == 0:
                val_sum = None
                val_avg = None
            else:
                val_sum = sum(vals)
                val_avg = val_sum / len(vals)

            out[f"{field_name}Sum"] = val_sum
            out[f"{field_name}Avg"] = val_avg

    return out

def resolve_field(z, info, *, z_field, **params):
    is_list = z_field | op_is_list | collect
    is_required = z_field | op_is_required | collect

    opts = internal_resolve_field(z, info, z_field)

    if is_list:
        opts = handle_list_params(opts, target(z_field), params, info)

    opts = collect(opts)

    if is_list:
        return opts
    else:
        if not is_required and len(opts) == 0:
            return None
        return single(opts)

def resolve_id(z, info):
    return str(origin_uid(z))


##############################
# * Mutations
#----------------------------
from threading import Lock
mutation_lock = Lock()

def resolve_add(_, info, *, type_node, **params):
    # TODO: @unique checks should probably be done post change as multiple adds
    # could try changing the same thing, including nested types.
    try:
        with mutation_lock:
            name_gen = NameGen()
            actions = []
            post_checks = []
            new_obj_names = []
            updated_objs = []

            # This is not optimal but simplest to understand for now.
            upsert = params.get("upsert", False)
            for item in params["input"]:
                # Check id fields to see if we already have this.
                if "id" in item:
                    if not upsert:
                        raise ExternalError("Can't update item with id without setting upsert")
                    obj = find_existing_entity_by_id(info, type_node, item["id"])
                    if obj is None:
                        raise Exception("Item doesn't exist")
                    set_d = {**item}
                    set_d.pop("id")
                    new_actions,new_post_checks = update_entity(obj, info, type_node, set_d, {}, name_gen)
                    actions += new_actions
                    post_checks += new_post_checks
                    updated_objs += [obj]
                else:
                    obj_name,more_actions,more_post_checks = add_new_entity(info, type_node, item, name_gen)
                    actions += more_actions
                    post_checks += more_post_checks
                    new_obj_names += [obj_name]

            r = commit_with_post_checks(actions, post_checks, info)

            ents = updated_objs + [r[name] for name in new_obj_names]
            # Note: we return the details after any updates
            ents = ents | map[now] | collect

            count = len(new_obj_names)

            return {"count": count, "ents": ents}
    except ExternalError:
        raise
    except Exception as exc:
        log.error("There was an error in resolve_add", exc_info=exc)
        raise Exception("Unexpected error")
            
def resolve_upfetch(_, info, *, type_node, **params):
    # TODO: @unique checks should probably be done post change as multiple adds
    # could try changing the same thing, including nested types.
    try:
        with mutation_lock:
            # Upfetch is a lot like add with upsert, except it uses the specially
            # indicated upfetch field to work on, rather than id.
            name_gen = NameGen()
            actions = []
            post_checks = []
            new_obj_names = []
            updated_objs = []

            upfetch_field = op_upfetch_field(type_node)
            field_name = upfetch_field | F.Name | collect

            for item in params["input"]:
                # Check the upfetch field to see if we already have this.
                if field_name not in item:
                    raise Exception("Should never get here, because the upfetch field should be marked as required")

                obj = find_existing_entity_by_field(info, type_node, upfetch_field, item[field_name])
                if obj is None:
                    obj_name,more_actions,more_post_checks = add_new_entity(info, type_node, item, name_gen)
                    actions += more_actions
                    post_checks += more_post_checks
                    new_obj_names += [obj_name]
                else:
                    new_actions,new_post_checks = update_entity(obj, info, type_node, item, {}, name_gen)
                    actions += new_actions
                    post_checks += new_post_checks
                    updated_objs += [obj]

            r = commit_with_post_checks(actions, post_checks, info)

            ents = updated_objs + [r[name] for name in new_obj_names]
            # Note: we return the details after any updates
            ents = ents | map[now] | collect
            count = len(new_obj_names)

            return {"count": count, "ents": ents}
    except ExternalError:
        raise
    except Exception as exc:
        log.error("There was an error in resolve_upfetch", exc_info=exc)
        raise Exception("Unexpected error")
            
        
def resolve_update(_, info, *, type_node, **params):
    # TODO: @unique checks should probably be done post change as multiple adds
    # could try changing the same thing, including nested types.
    try:
        with mutation_lock:
            if "input" not in params or "filter" not in params["input"]:
                raise Exception("Not allowed to update everything!")
            ents = resolve_query(_, info, type_node=type_node, filter=params["input"]["filter"])

            actions = []
            post_checks = []

            name_gen = NameGen()
            for ent in ents:
                new_actions,new_post_checks = update_entity(ent, info, type_node, params["input"].get("set", {}), params["input"].get("remove", {}), name_gen)
                actions += new_actions
                post_checks += new_post_checks

            commit_with_post_checks(actions, post_checks, info)

            count = len(ents)

            # Note: we return the details after the update
            ents = ents | map[now] | collect

            return {"count": count, "ents": ents}
    except ExternalError:
        raise
    except Exception as exc:
        log.error("There was an error in resolve_update", exc_info=exc)
        raise Exception("Unexpected error")

def resolve_delete(_, info, *, type_node, **params):
    try:
        with mutation_lock:
            # Do the same thing as a resolve_query but delete the entities instead.
            if "filter" not in params:
                raise ExtenalError("Not allowed to delete everything!")
            ents = resolve_query(_, info, type_node=type_node, **params)

            if not ents | map[pass_delete_auth[type_node][info]] | all | collect:
                raise ExtenalError("Auth check returned False")

            post_checks = []
            for ent in ents:
                post_checks += [("remove", ent, type_node)]
            actions = [terminate(ent) for ent in ents]
            r = commit_with_post_checks(actions, post_checks, info)

            count = len(ents)

            return {"count": count, "ents": ents}
    except ExternalError:
        raise
    except Exception as exc:
        log.error("There was an error in resolve_delete", exc_info=exc)
        raise Exception("Unexpected error")

def resolve_filter_response(obj, info, *, type_node, **params):
    ents = obj["ents"]

    ents = handle_list_params(ents, type_node, params, info)

    return ents | collect




##############################################
# * Internal query parts
#--------------------------------------------

def obtain_initial_list(type_node, filter_opts, info):
    gs = info.context["gs"]

    type_et = ET(type_node | Out[RT.GQL_Delegate] | collect)
    if filter_opts is not None and filter_opts.get("id", None) is not None:
        # ids were provided, so the initial list starts with them

        # Note: we make the decision here to not throw on a missing id, as that
        # could potentially be exploited somehow by smoeone to learn about what
        # items exist even if they don't have auth access. A missing id is hence
        # just "not passing" the filter.

        log.debug("In the explicit ID path")

        ids = filter_opts["id"]
        zs = []

        zs = (ids
              | map[lambda id: find_existing_entity_by_id(info, type_node, id)]
              | filter[Not[equals[None]]])

        if info.context["debug_level"] >= 3:
            log.debug("DEBUG 3: built initial list from ids", length_ids=len(ids), length_list=length(zs))

        return zs
    else:
        zs = gs | all[type_et] | filter[pass_query_auth[type_node][info]]
        if info.context["debug_level"] >= 3:
            log.debug("DEBUG 3: built initial list from type and auth", length_list=length(zs))
        return zs

    

def handle_list_params(opts, z_node, params, info):
    opts = maybe_filter_result(opts, z_node, info, params.get("filter", None))
    if info.context["debug_level"] >= 3:
        log.debug("DEBUG 3: after filtering", length_list=length(opts))
    opts = maybe_sort_result(opts, z_node, info, params.get("order", None))
    opts = maybe_paginate_result(opts, params.get("first", None), params.get("offset", None))
    return opts

@func
def field_resolver_by_name(z, type_node, info, name):
    # Note name goes last because it is curried last... this is weird
    if name == "id":
        return resolve_id(z, info=info)
    sub_field = get_field_rel_by_name(type_node, name)
    return resolve_field(z, info=info, z_field=sub_field)


# ** Filtering

def maybe_filter_result(opts, z_node, info, fil=None):
    if fil is None:
        return opts

    temp_fil = build_filter_zefop(fil, z_node, info)
    if info.context["debug_level"] >= 4:
        log.debug("DEBUG 4: filter is", fil=temp_fil)
        temp_fil = (apply[identity, temp_fil]
                    | tap[match[
                        (Is[second], lambda x: log.debug("DEBUG 4: filter passed", item=first(x))),
                        (Any, lambda x: log.debug("DEBUG 4: filter failed", item=first(x)))
                        ]]
                    | second)
    return opts | filter[temp_fil]

def build_filter_zefop(fil, z_node, info):
    field_resolver = field_resolver_by_name[z_node][info]
    # top level is ands
    top = And
    for key,sub in fil.items():
        if key == "and":
            this = And
            for part in sub:
                this = this[build_filter_zefop(part, z_node, info)]
        elif key == "or":
            this = Or
            for part in sub:
                this = this[build_filter_zefop(part, z_node, info)]
        elif key == "not":
            this = Not[build_filter_zefop(sub, z_node, info)]
        elif key == "id":
            # This is handled specially - functions like an "in".
            val = field_resolver["id"]
            this = val | contained_in[sub]
        else:
            # This must be a field
            z_field = get_field_rel_by_name(z_node, key)
            z_field_node = target(z_field)

            val = field_resolver[key]
            if op_is_list(z_field):
                list_top = And
                for list_key,list_sub in sub.items():
                    if list_key == "any":
                        sub_fil = build_filter_zefop(list_sub, z_field_node, info)
                        list_top = list_top[val | map[sub_fil] | any]
                    elif list_key == "all":
                        sub_fil = build_filter_zefop(list_sub, z_field_node, info)
                        list_top = list_top[val | map[sub_fil] | all]
                    elif list_key == "size":
                        temp = val | length | scalar_comparison_op(list_sub)
                        list_top = list_top[temp]
                    else:
                        raise Exception(f"Unknown list filter keyword: {list_key}")
                this = list_top
            elif op_is_scalar(z_field_node):
                if isinstance(sub, bool):
                    this = val | equals[sub]
                else:
                    this = val | scalar_comparison_op(sub)
            else:
                sub_fil = build_filter_zefop(sub, z_field_node, info)
                this = val | And[Not[equals[None]]][sub_fil]


        top = top[this]

    return top

def scalar_comparison_op(sub):
    this = And[Not[equals[None]]]
    for scalar_key,scalar_sub in sub.items():
        if scalar_key == "eq":
            this = this[equals[scalar_sub]]
        elif scalar_key == "in":
            this = this[contained_in[scalar_sub]]
        elif scalar_key == "contains":
            this = this[contains[scalar_sub]]
        elif scalar_key == "le":
            this = this[less_than_or_equal[scalar_sub]]
        elif scalar_key == "lt":
            this = this[less_than[scalar_sub]]
        elif scalar_key == "ge":
            this = this[greater_than_or_equal[scalar_sub]]
        elif scalar_key == "gt":
            this = this[greater_than[scalar_sub]]
        elif scalar_key == "between":
            this = this[greater_than_or_equal[scalar_sub["min"]]]
            this = this[less_than_or_equal[scalar_sub["max"]]]
        else:
            raise Exception(f"Unknown comparison operator: {key}")
    return this
                
def get_field_rel_by_name(z_type, name):
    return (z_type | out_rels[RT.GQL_Field]
            | filter[Z | F.Name | equals[name]]
            | first
            | collect)

# ** Sorting

def maybe_sort_result(opts, z_node, info, sort_decl=None):
    if sort_decl is None:
        return opts

    field_resolver = field_resolver_by_name[z_node][info]

    # First, get the list of things to sort by, so that we can reverse it
    sort_list = []
    cur = sort_decl
    while cur is not None:
        if "asc" in cur:
            assert not "desc" in cur
            val = field_resolver[cur["asc"]]
            sort_list += [sort[val]]
        elif "desc" in cur:
            val = field_resolver[cur["desc"]]
            sort_list += [sort[val][True]]

        cur = cur.get("then", None)

    sort_list.reverse()

    for action in sort_list:
        opts = opts | action

    return opts

# ** Pagination

def maybe_paginate_result(opts, first=None, offset=None):
    if offset is not None:
        opts = opts | skip[offset]
    if first is not None:
        opts = opts | take[first]
    return opts


# ** Resolution

@func
def internal_resolve_field(z, info, z_field, auth_required=True):
    # This returns a LazyValue so we can deal with whatever comes out without
    # instantiating the whole list.

    # Also *only* returns that list. The calling function needs to apply the single/list logic
    
    is_incoming = z_field | op_is_incoming | collect
    # This is a delegate
    if z_field | has_out[RT.GQL_Resolve_With] | collect:
        relation = z_field | Out[RT.GQL_Resolve_With] | collect
        is_triple = source(relation) != relation

        rt = RT(relation)

        if is_triple:
            if is_incoming:
                assert rae_type(z) == rae_type(target(relation)), f"The RAET of the object {z} is not the same as that of the delegate relation {target(relation)}"
            else:
                assert rae_type(z) == rae_type(source(relation)), f"The RAET of the object {z} is not the same as that of the delegate relation {source(relation)}"

        if is_incoming:
            opts = z | Ins[rt]
            if is_triple:
                opts = opts | filter[is_a[rae_type(source(relation))]]
        else:
            opts = z | Outs[rt]
            if is_triple:
                opts = opts | filter[is_a[rae_type(target(relation))]]
    elif z_field | has_out[RT.GQL_FunctionResolver] | collect:
        opts = func[z_field | Out[RT.GQL_FunctionResolver] | collect](z, info)
        # This is to mimic the behaviour that people probably expect from a
        # non-list resolver.
        if type(opts) not in [list,tuple]:
            if opts is None:
                opts = []
            else:
                opts = [opts]
    else:
        raise Exception(f"Don't know how to resolve this field: {z_field}")

    if auth_required:
        opts = opts | filter[pass_query_auth[target(z_field)][info]]

    # We must convert final objects from AEs to python types.
    # if z_field | target | is_core_scalar | collect:
    if z_field | target | op_is_scalar | collect:
        # With a dynamic resolver, the items could also be values, so only apply value if they are ZefRefs
        opts = opts | map[match[
            (ZefRef, value),
            (Any, identity)
        ]]

    return opts


# ** Handling adding

def NameGen():
    n = 0
    while True:
        n += 1
        yield n

def find_existing_entity_by_id(info, type_node, id):
    if id is None:
        return None
    the_uid = uid(id)
    if the_uid is None:
        raise Exception("An id of {id} cannot be converted to a uid.")
    
    gs = info.context["gs"]

    et = ET(type_node | Out[RT.GQL_Delegate] | collect)
    ent = gs[uid(id)] | collect
    if not is_a(ent, et):
        return None
    if not ent | pass_query_auth[type_node][info] | collect:
        return None

    return ent

def find_existing_entity_by_field(info, type_node, z_field, val):
    if val is None:
        raise Exception("Can't find an entity by a None field value")

    gs = info.context["gs"]
    et = ET(type_node | Out[RT.GQL_Delegate] | collect)

    # Note: we filter out with query auth even though this may mean we return
    # None instead of the actual entity. The follow-up logic with an upfetch
    # might seem wrong, as it would try to create the same item again. However,
    # because the field is also @unique then this will fail. Better to keep the
    # failure point at the same location so we can determine what kind of error
    # to return and whether this will leak sensitive information.
    ent = (gs | all[et] | filter[pass_query_auth[type_node][info]]
           | filter[internal_resolve_field[info][z_field] | optional | equals[val]]
           | optional
           | collect)

    return ent

def add_new_entity(info, type_node, params, name_gen):

    actions = []
    post_checks = []

    this = str(next(name_gen))
    type_name = type_node | F.Name | collect

    post_checks += [("add", this, type_node)]

    et = ET(type_node | Out[RT.GQL_Delegate] | collect)
    actions += [et[this]]

    # This should probably be cached
    field_mapping = {}
    for z_field in type_node | out_rels[RT.GQL_Field]:
        field_name = z_field | F.Name | collect
        field_mapping[field_name] = z_field
        # Convenient spot to validate that required fields have been specified.
        if op_is_required(z_field):
            if field_name not in params:
                raise ExternalError(f"Required field '{field_name}' not given when creating new entity of type '{type_name}'")


    for key,val in params.items():
        # TODO: Validate that any unique field is not duplicated
        z_field = field_mapping[key]
        field_name = z_field | F.Name | collect
        rt = RT(z_field | Out[RT.GQL_Resolve_With] | collect)
        if z_field | op_is_list | collect:
            if not isinstance(val, list):
                raise Exception(f"Value should have been list but was {type(val)}")

        if z_field | target | op_is_scalar | collect:
            if op_is_unique(z_field):
                others = info.context["gs"] | all[et] | filter[fvalue[rt][None] | equals[val]] | func[set] | collect
                if len(others) > 0:
                    log.error("Trying to add a new entity with unique field that conflicts with others", et=et, field=field_name, others=others)
                    raise ExternalError(f"Unique field '{field_name}' conflicts with existing items.")
            if z_field | op_is_list | collect:
                l = val
            else:
                l = [val]

            for item in l:
                # TODO: Maybe proper ordering here too? Or should this
                # always be considered to be a set, ordered only when the
                # client requests it?
                if z_field | op_is_incoming | collect:
                    actions += [item, rt, (Z[this])]
                else:
                    actions += [(Z[this], rt, item)]
        else:
            if z_field | op_is_list | collect:
                l = val
            else:
                l = [val]

            for item in l:
                obj,obj_actions,obj_post_checks = find_or_add_entity(item, info, target(z_field), name_gen)
                actions += obj_actions
                post_checks += obj_post_checks
                if z_field | op_is_incoming | collect:
                    actions += [(obj, rt, Z[this])]
                else:
                    actions += [(Z[this], rt, obj)]

    return this, actions, post_checks

def find_or_add_entity(val, info, target_node, name_gen):
    if isinstance(val, dict) and val.get("id", None) is not None:
        # There should be no other fields given for this entity, otherwise the meaning is unclear.
        if set(val.keys()) != {"id"}:
            raise ExternalError("An entity should be designated with either an 'id' or a set of new fields to create a new entity.")
        obj = find_existing_entity_by_id(info, target_node, val["id"])
        if obj is None:
            raise ExternalError(f"Unable to find entity of kind '{target_node | F.Name | collect}' with id '{val['id']}'.")
        return obj,[],[]
    else:
        obj_name,actions,post_checks = add_new_entity(info, target_node, val, name_gen)
        return Z[obj_name], actions, post_checks
    

def update_entity(z, info, type_node, set_d, remove_d, name_gen):
    type_name = type_node | F.Name | collect

    # Refuse to set and remove the same thing. Just too confusing to deal with
    assert(len(set(set_d.keys()).intersection(remove_d.keys())) == 0), "Can't have the same set/remove keys"
    if len(set_d) + len(remove_d) == 0:
        raise ExternalError("No set or remove in update_entity!")

    # This is the pre-update auth only
    # TODO: Post-update auth
    if not pass_pre_update_auth(z, type_node, info):
        raise ExternalError("Not allowed to update")

    actions = []
    post_checks = []
    post_checks += [("update", z, type_node)]

    # This should probably be cached
    field_mapping = {}
    for z_field in type_node | out_rels[RT.GQL_Field]:
        field_mapping[z_field | F.Name | collect] = z_field

    for key,val in set_d.items():
        # TODO: Validate that any unique field is not duplicated
        z_field = field_mapping[key]
        field_name = z_field | F.Name | collect
        # TODO: This should be able to distinguish based on the triple, not just the RT
        rt = RT(z_field | Out[RT.GQL_Resolve_With] | collect)

        if op_is_list(z_field):
            raise Exception(f"Updating list things is a todo (for z_field={z_field})")
        else:
            if op_is_unique(z_field):
                # This used to be checked directly, here but just in case
                # there's a mutation that renames two things at the same time,
                # we change this up a bit.
                post_checks += [("unique", z_field, type_node)]

            if z_field | target | op_is_scalar | collect:
                actions += [z | set_field[rt][val][op_is_incoming(z_field)]]
            else:
                found_z,new_actions,new_post_checks = find_or_add_entity(val, info, target(z_field), name_gen)
                actions += new_actions
                post_checks += new_post_checks

                actions += [z | set_field[rt][found_z][op_is_incoming(z_field)]]
    
    for key,val in remove_d.items():
        if val is not None:
            raise ExternalError("Remove vals need to be nil")
        z_field = field_mapping[key]
        field_name = z_field | F.Name | collect
        if op_is_required(z_field):
            raise ExternalError(f"Not allowed to remove required field '{field_name}' on type '{type_name}'")
        # TODO: This should be able to distinguish based on the triple, not just the RT
        rt = RT(z_field | Out[RT.GQL_Resolve_With] | collect)
        if op_is_incoming(z_field):
            rels = z | in_rels[rt]
        else:
            rels = z | out_rels[rt]
        actions += [terminate(rel) for rel in rels]

        # TODO: Add a post-check here that this would not remove a relation on a
        # type that has a required relation. Note that a new relation could be
        # created in the same transaction, so it needs to be post, not directly
        # here.

        # Also delete scalars
        if z_field | target | op_is_scalar | collect:
            actions += [terminate(target(rel)) for rel in rels]

    return actions, post_checks


##############################
# * Auth things
#----------------------------

def pass_auth_generic(z, schema_node, info, rt_list):
    to_call = None
    for rt in rt_list:
        to_call = schema_node | Outs[rt] | optional | collect
        if to_call is not None:
            break
    else:
        return True

    # TODO: Later on these will be zef functions so easier to call
    return temporary__call_string_as_func(
        to_call | value | collect,
        z=z,
        info=info,
        type_node=schema_node
    )

@func
def pass_query_auth(z, schema_node, info):
    return pass_auth_generic(z, schema_node, info, [RT.AllowQuery])

@func
def pass_add_auth(z, schema_node, info):
    return pass_auth_generic(z, schema_node, info, [RT.AllowAdd, RT.AllowQuery])

@func
def pass_pre_update_auth(z, schema_node, info):
    return pass_auth_generic(z, schema_node, info, [RT.AllowUpdate, RT.AllowQuery])

@func
def pass_post_update_auth(z, schema_node, info):
    return pass_auth_generic(z, schema_node, info, [RT.AllowUpdatePost, RT.AllowUpdate, RT.AllowQuery])

@func
def pass_delete_auth(z, schema_node, info):
    return pass_auth_generic(z, schema_node, info, [RT.AllowDelete, RT.AllowUpdate, RT.AllowQuery])

def temporary__call_string_as_func(s, **kwds):
    from ... import core, ops
    try:
        out = eval(
            s, {
                **{name: getattr(core,name) for name in dir(core) if not name.startswith("_")},
                **{name: getattr(ops,name) for name in dir(ops) if not name.startswith("_")},
                "auth_field": P(auth_helper_auth_field, **kwds),
            },
            kwds
        )
    except Exception as exc:
        log.error("Problem calling auth expression", expr=s, exc_info=exc, kwds=kwds)
        return False

    if isinstance(out, LazyValue):
        out = collect(out)
    elif isinstance(out, ZefOp):
        out = out(kwds.get("z", None))

    return out

def auth_helper_auth_field(field_name, auth, *, z, type_node, info):
    # A helper function for graphql schema, that requests an auth check of the
    # given kind on one of its fields.

    # Only makes sense for fields that are required, such as a user field.
    try:
        z_field = get_field_rel_by_name(type_node, field_name)
        z_field_node = target(z_field)
        val = field_resolver_by_name(z, type_node, info, field_name)
    except:
        # Going to assume this is because traversal failed auth along the way somewhere.
        log.error("auth_field helper got an exception, assuming failure of auth")
        return False

    if val is None:
        # This is something we can't query on, so therefore the query has failed.
        return False

    if auth == "query":
        func = pass_query_auth
    elif auth == "add":
        func = pass_add_auth
    elif auth == "update":
        func = pass_pre_update_auth
    elif auth == "updatePost":
        func = pass_post_update_auth
    elif auth == "delete":
        func = pass_delete_auth
    else:
        raise Exception(f"Don't understand auth type '{auth}' in auth_helper_auth_field")

    return func(val, z_field_node, info)



def commit_with_post_checks(actions, post_checks, info):
    g = Graph(info.context["gs"])
    with Transaction(g):
        try:
            r = actions | transact[g] | run
            # Test all post checks
            for (kind,obj,type_node) in post_checks:
                type_name = type_node | fvalue[RT.Name][''] | collect

                if kind in ["unique"]:
                    pass
                else:
                    if type(obj) == str:
                        obj = r[obj]
                    assert type(obj) == ZefRef
                    obj = obj | in_frame[g | now | collect][allow_tombstone] | collect

                if kind == "add":
                    for z_func in type_node | Outs[RT.OnCreate]:
                        try:
                            func[z_func](obj)
                        except:
                            raise ExternalError(f"OnCreate hook for type_node of '{type_name}' threw an exception")
                    if not pass_add_auth(obj, type_node, info):
                        raise ExternalError(f"Add auth check for type_node of '{type_name}' returned False")
                elif kind == "update":
                    for z_func in type_node | Outs[RT.OnUpdate]:
                        try:
                            func[z_func](obj)
                        except:
                            raise ExternalError(f"OnUpdate hook for type_node of '{type_name}' threw an exception")
                    if not pass_post_update_auth(obj, type_node, info):
                        raise ExternalError(f"Post-update auth check for type_node of '{type_name}' returned False")
                elif kind == "remove":
                    for z_func in type_node | Outs[RT.OnRemove]:
                        try:
                            func[z_func](obj)
                        except:
                            raise ExternalError(f"OnRemove hook for type_node of '{type_name}' threw an exception")
                elif kind == "unique":
                    print("Doing a unqiue check for", obj, type_name)
                    # In this case, obj is the field which must be unique
                    z_field = obj
                    assert op_is_unique(z_field)
                    # Get all values - note this is not filtered by the user's
                    # viewpoint, so we need to be a little careful.
                    ents = g | now | all[ET(type_node | Out[RT.GQL_Delegate] | collect)]
                    vals = ents | map[internal_resolve_field[info][z_field][False]] | concat | collect

                    dis = distinct(vals)
                    print(vals)
                    print(dis)
                    if len(dis) != len(vals):
                        log.error("Non-unique values", vals=set(vals) - set(dis))
                        raise ExternalError(f"Non-unique values found for field '{z_field | F.Name | collect}' of type_node '{type_name}'")


        except Exception as exc:
            log.error("Aborting transaction",
                      exc_info=exc)
            from ...pyzef.internals import AbortTransaction
            AbortTransaction(g)
            if type(exc) == ExternalError:
                raise exc
            else:
                raise ExternalError("Unexpected error in auth check/hooks execution")

    return r
