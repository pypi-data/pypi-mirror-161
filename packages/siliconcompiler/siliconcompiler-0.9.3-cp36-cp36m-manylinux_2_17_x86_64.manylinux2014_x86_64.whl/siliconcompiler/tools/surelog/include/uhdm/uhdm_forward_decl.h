// -*- c++ -*-

/*

 Copyright 2019-2020 Alain Dargelas

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

/*
 * File:   uhdm_forward_decl.h
 * Author:
 *
 * Created on May 06, 2020, 10:03 PM
 */

#ifndef UHDM_FORWARD_DECL_CLASS_H
#define UHDM_FORWARD_DECL_CLASS_H

#include <vector>

namespace UHDM {
class BaseClass;
typedef BaseClass any;
typedef std::vector<BaseClass*> VectorOfany;
class ordered_wait;
class enum_const;
class reg;
class chandle_var;
class cont_assign;
class switch_array;
class table_entry;
class enum_typespec;
class property_inst;
class byte_var;
class clocked_seq;
class typespec;
class event_typespec;
class named_event;
class repeat_control;
class let_decl;
class disable_fork;
class any_pattern;
class param_assign;
class assume;
class integer_var;
class user_systf;
class string_var;
class clocking_io_decl;
class short_int_var;
class tf_call;
class function;
class ports;
class implication;
class case_stmt;
class int_var;
class atomic_stmt;
class package;
class logic_var;
class if_else;
class alias_stmt;
class class_defn;
class module_array;
class constraint_ordering;
class for_stmt;
class case_property_item;
class part_select;
class force;
class sequence_decl;
class named_begin;
class constraint_expr;
class disable;
class indexed_part_select;
class gate_array;
class unsupported_stmt;
class always;
class integer_typespec;
class array_typespec;
class hier_path;
class wait_fork;
class bit_var;
class class_obj;
class primitive;
class net_loads;
class tchk_term;
class interface;
class return_stmt;
class disables;
class property_typespec;
class design;
class dist_item;
class bit_typespec;
class struct_var;
class modport;
class array_net;
class forever_stmt;
class interface_tf_decl;
class short_real_var;
class port_bit;
class chandle_typespec;
class immediate_assume;
class net_drivers;
class method_func_call;
class operation;
class case_item;
class assign_stmt;
class property_decl;
class named_fork;
class distribution;
class prop_formal_decl;
class import;
class if_stmt;
class switch_tran;
class seq_formal_decl;
class null_stmt;
class let_expr;
class enum_net;
class method_task_call;
class process_stmt;
class def_param;
class spec_param;
class typespec_member;
class deassign;
class class_var;
class var_select;
class gen_scope_array;
class tagged_pattern;
class gate;
class task;
class named_event_array;
class immediate_cover;
class time_net;
class var_bit;
class io_decl;
class interface_array;
class primitive_array;
class short_real_typespec;
class immediate_assert;
class parameter;
class attribute;
class port;
class program_array;
class while_stmt;
class repeat;
class fork_stmt;
class struct_typespec;
class gen_var;
class packed_array_net;
class final_stmt;
class constant;
class delay_control;
class property_spec;
class prim_term;
class expect_stmt;
class event_control;
class class_typespec;
class path_term;
class sequence_typespec;
class constr_if_else;
class restrict;
class byte_typespec;
class extends;
class real_var;
class virtual_interface_var;
class ref_obj;
class constr_foreach;
class release;
class type_parameter;
class task_func;
class func_call;
class cover;
class array_var;
class variables;
class scope;
class wait_stmt;
class integer_net;
class constraint;
class interface_typespec;
class cont_assign_bit;
class void_typespec;
class unsupported_expr;
class udp_array;
class program;
class union_var;
class tchk;
class nets;
class range;
class bit_select;
class module;
class long_int_typespec;
class soft_disable;
class case_property;
class simple_expr;
class clocked_property;
class struct_pattern;
class logic_net;
class task_call;
class assert_stmt;
class logic_typespec;
class break_stmt;
class sys_func_call;
class enum_var;
class unsupported_typespec;
class constr_if;
class net;
class int_typespec;
class waits;
class packed_array_typespec;
class union_typespec;
class event_stmt;
class gen_scope;
class ref_var;
class udp_defn;
class net_bit;
class delay_term;
class sequence_inst;
class short_int_typespec;
class time_var;
class thread_obj;
class initial;
class do_while;
class string_typespec;
class sys_task_call;
class mod_path;
class foreach_stmt;
class assignment;
class struct_net;
class time_typespec;
class continue_stmt;
class packed_array_var;
class instance_array;
class reg_array;
class begin;
class instance;
class expr;
class real_typespec;
class udp;
class long_int_var;
class clocking_block;
class concurrent_assertions;
class multiclock_sequence_expr;

};


#endif
