// -*- c++ -*-

/*

 Copyright 2019 Alain Dargelas

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
 * File:   VpiListener.h
 * Author: alaindargelas
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_VPILISTENER_CLASS_H
#define UHDM_VPILISTENER_CLASS_H

#include <uhdm/uhdm_forward_decl.h>
#include <uhdm/vpi_user.h>

namespace UHDM {
class VpiListener {
public:
  // Use implicit constructor to initialize all members
  // VpiListener()

  virtual ~VpiListener() {}

    virtual void enterOrdered_wait(const ordered_wait* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveOrdered_wait(const ordered_wait* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterEnum_const(const enum_const* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveEnum_const(const enum_const* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterReg(const reg* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveReg(const reg* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterChandle_var(const chandle_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveChandle_var(const chandle_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterCont_assign(const cont_assign* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveCont_assign(const cont_assign* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSwitch_array(const switch_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSwitch_array(const switch_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTable_entry(const table_entry* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTable_entry(const table_entry* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterEnum_typespec(const enum_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveEnum_typespec(const enum_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProperty_inst(const property_inst* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProperty_inst(const property_inst* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterByte_var(const byte_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveByte_var(const byte_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClocked_seq(const clocked_seq* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClocked_seq(const clocked_seq* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTypespec(const typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTypespec(const typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterEvent_typespec(const event_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveEvent_typespec(const event_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNamed_event(const named_event* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNamed_event(const named_event* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterRepeat_control(const repeat_control* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveRepeat_control(const repeat_control* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterLet_decl(const let_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveLet_decl(const let_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDisable_fork(const disable_fork* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDisable_fork(const disable_fork* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAny_pattern(const any_pattern* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAny_pattern(const any_pattern* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterParam_assign(const param_assign* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveParam_assign(const param_assign* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAssume(const assume* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAssume(const assume* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInteger_var(const integer_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInteger_var(const integer_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUser_systf(const user_systf* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUser_systf(const user_systf* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterString_var(const string_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveString_var(const string_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClocking_io_decl(const clocking_io_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClocking_io_decl(const clocking_io_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterShort_int_var(const short_int_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveShort_int_var(const short_int_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTf_call(const tf_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTf_call(const tf_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterFunction(const function* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveFunction(const function* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPorts(const ports* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePorts(const ports* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterImplication(const implication* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveImplication(const implication* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterCase_stmt(const case_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveCase_stmt(const case_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInt_var(const int_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInt_var(const int_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAtomic_stmt(const atomic_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAtomic_stmt(const atomic_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPackage(const package* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePackage(const package* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterLogic_var(const logic_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveLogic_var(const logic_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterIf_else(const if_else* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveIf_else(const if_else* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAlias_stmt(const alias_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAlias_stmt(const alias_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClass_defn(const class_defn* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClass_defn(const class_defn* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterModule_array(const module_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveModule_array(const module_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConstraint_ordering(const constraint_ordering* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConstraint_ordering(const constraint_ordering* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterFor_stmt(const for_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveFor_stmt(const for_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterCase_property_item(const case_property_item* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveCase_property_item(const case_property_item* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPart_select(const part_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePart_select(const part_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterForce(const force* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveForce(const force* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSequence_decl(const sequence_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSequence_decl(const sequence_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNamed_begin(const named_begin* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNamed_begin(const named_begin* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConstraint_expr(const constraint_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConstraint_expr(const constraint_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDisable(const disable* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDisable(const disable* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterIndexed_part_select(const indexed_part_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveIndexed_part_select(const indexed_part_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterGate_array(const gate_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveGate_array(const gate_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUnsupported_stmt(const unsupported_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUnsupported_stmt(const unsupported_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAlways(const always* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAlways(const always* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInteger_typespec(const integer_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInteger_typespec(const integer_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterArray_typespec(const array_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveArray_typespec(const array_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterHier_path(const hier_path* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveHier_path(const hier_path* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterWait_fork(const wait_fork* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveWait_fork(const wait_fork* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterBit_var(const bit_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveBit_var(const bit_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClass_obj(const class_obj* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClass_obj(const class_obj* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPrimitive(const primitive* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePrimitive(const primitive* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNet_loads(const net_loads* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNet_loads(const net_loads* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTchk_term(const tchk_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTchk_term(const tchk_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInterface(const interface* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInterface(const interface* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterReturn_stmt(const return_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveReturn_stmt(const return_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDisables(const disables* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDisables(const disables* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProperty_typespec(const property_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProperty_typespec(const property_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDesign(const design* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDesign(const design* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDist_item(const dist_item* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDist_item(const dist_item* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterBit_typespec(const bit_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveBit_typespec(const bit_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterStruct_var(const struct_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveStruct_var(const struct_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterModport(const modport* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveModport(const modport* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterArray_net(const array_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveArray_net(const array_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterForever_stmt(const forever_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveForever_stmt(const forever_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInterface_tf_decl(const interface_tf_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInterface_tf_decl(const interface_tf_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterShort_real_var(const short_real_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveShort_real_var(const short_real_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPort_bit(const port_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePort_bit(const port_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterChandle_typespec(const chandle_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveChandle_typespec(const chandle_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterImmediate_assume(const immediate_assume* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveImmediate_assume(const immediate_assume* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNet_drivers(const net_drivers* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNet_drivers(const net_drivers* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterMethod_func_call(const method_func_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveMethod_func_call(const method_func_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterOperation(const operation* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveOperation(const operation* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterCase_item(const case_item* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveCase_item(const case_item* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAssign_stmt(const assign_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAssign_stmt(const assign_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProperty_decl(const property_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProperty_decl(const property_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNamed_fork(const named_fork* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNamed_fork(const named_fork* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDistribution(const distribution* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDistribution(const distribution* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProp_formal_decl(const prop_formal_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProp_formal_decl(const prop_formal_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterImport(const import* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveImport(const import* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterIf_stmt(const if_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveIf_stmt(const if_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSwitch_tran(const switch_tran* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSwitch_tran(const switch_tran* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSeq_formal_decl(const seq_formal_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSeq_formal_decl(const seq_formal_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNull_stmt(const null_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNull_stmt(const null_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterLet_expr(const let_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveLet_expr(const let_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterEnum_net(const enum_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveEnum_net(const enum_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterMethod_task_call(const method_task_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveMethod_task_call(const method_task_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProcess_stmt(const process_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProcess_stmt(const process_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDef_param(const def_param* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDef_param(const def_param* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSpec_param(const spec_param* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSpec_param(const spec_param* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTypespec_member(const typespec_member* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTypespec_member(const typespec_member* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDeassign(const deassign* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDeassign(const deassign* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClass_var(const class_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClass_var(const class_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterVar_select(const var_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveVar_select(const var_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterGen_scope_array(const gen_scope_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveGen_scope_array(const gen_scope_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTagged_pattern(const tagged_pattern* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTagged_pattern(const tagged_pattern* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterGate(const gate* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveGate(const gate* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTask(const task* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTask(const task* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNamed_event_array(const named_event_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNamed_event_array(const named_event_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterImmediate_cover(const immediate_cover* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveImmediate_cover(const immediate_cover* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTime_net(const time_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTime_net(const time_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterVar_bit(const var_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveVar_bit(const var_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterIo_decl(const io_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveIo_decl(const io_decl* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInterface_array(const interface_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInterface_array(const interface_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPrimitive_array(const primitive_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePrimitive_array(const primitive_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterShort_real_typespec(const short_real_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveShort_real_typespec(const short_real_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterImmediate_assert(const immediate_assert* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveImmediate_assert(const immediate_assert* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterParameter(const parameter* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveParameter(const parameter* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAttribute(const attribute* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAttribute(const attribute* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPort(const port* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePort(const port* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProgram_array(const program_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProgram_array(const program_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterWhile_stmt(const while_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveWhile_stmt(const while_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterRepeat(const repeat* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveRepeat(const repeat* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterFork_stmt(const fork_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveFork_stmt(const fork_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterStruct_typespec(const struct_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveStruct_typespec(const struct_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterGen_var(const gen_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveGen_var(const gen_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPacked_array_net(const packed_array_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePacked_array_net(const packed_array_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterFinal_stmt(const final_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveFinal_stmt(const final_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConstant(const constant* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConstant(const constant* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDelay_control(const delay_control* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDelay_control(const delay_control* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProperty_spec(const property_spec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProperty_spec(const property_spec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPrim_term(const prim_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePrim_term(const prim_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterExpect_stmt(const expect_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveExpect_stmt(const expect_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterEvent_control(const event_control* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveEvent_control(const event_control* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClass_typespec(const class_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClass_typespec(const class_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPath_term(const path_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePath_term(const path_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSequence_typespec(const sequence_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSequence_typespec(const sequence_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConstr_if_else(const constr_if_else* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConstr_if_else(const constr_if_else* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterRestrict(const restrict* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveRestrict(const restrict* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterByte_typespec(const byte_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveByte_typespec(const byte_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterExtends(const extends* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveExtends(const extends* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterReal_var(const real_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveReal_var(const real_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterVirtual_interface_var(const virtual_interface_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveVirtual_interface_var(const virtual_interface_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterRef_obj(const ref_obj* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveRef_obj(const ref_obj* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConstr_foreach(const constr_foreach* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConstr_foreach(const constr_foreach* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterRelease(const release* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveRelease(const release* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterType_parameter(const type_parameter* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveType_parameter(const type_parameter* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTask_func(const task_func* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTask_func(const task_func* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterFunc_call(const func_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveFunc_call(const func_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterCover(const cover* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveCover(const cover* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterArray_var(const array_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveArray_var(const array_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterVariables(const variables* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveVariables(const variables* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterScope(const scope* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveScope(const scope* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterWait_stmt(const wait_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveWait_stmt(const wait_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInteger_net(const integer_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInteger_net(const integer_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConstraint(const constraint* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConstraint(const constraint* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInterface_typespec(const interface_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInterface_typespec(const interface_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterCont_assign_bit(const cont_assign_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveCont_assign_bit(const cont_assign_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterVoid_typespec(const void_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveVoid_typespec(const void_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUnsupported_expr(const unsupported_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUnsupported_expr(const unsupported_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUdp_array(const udp_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUdp_array(const udp_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterProgram(const program* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveProgram(const program* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUnion_var(const union_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUnion_var(const union_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTchk(const tchk* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTchk(const tchk* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNets(const nets* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNets(const nets* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterRange(const range* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveRange(const range* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterBit_select(const bit_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveBit_select(const bit_select* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterModule(const module* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveModule(const module* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterLong_int_typespec(const long_int_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveLong_int_typespec(const long_int_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSoft_disable(const soft_disable* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSoft_disable(const soft_disable* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterCase_property(const case_property* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveCase_property(const case_property* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSimple_expr(const simple_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSimple_expr(const simple_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClocked_property(const clocked_property* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClocked_property(const clocked_property* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterStruct_pattern(const struct_pattern* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveStruct_pattern(const struct_pattern* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterLogic_net(const logic_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveLogic_net(const logic_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTask_call(const task_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTask_call(const task_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAssert_stmt(const assert_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAssert_stmt(const assert_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterLogic_typespec(const logic_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveLogic_typespec(const logic_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterBreak_stmt(const break_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveBreak_stmt(const break_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSys_func_call(const sys_func_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSys_func_call(const sys_func_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterEnum_var(const enum_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveEnum_var(const enum_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUnsupported_typespec(const unsupported_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUnsupported_typespec(const unsupported_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConstr_if(const constr_if* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConstr_if(const constr_if* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNet(const net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNet(const net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInt_typespec(const int_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInt_typespec(const int_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterWaits(const waits* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveWaits(const waits* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPacked_array_typespec(const packed_array_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePacked_array_typespec(const packed_array_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUnion_typespec(const union_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUnion_typespec(const union_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterEvent_stmt(const event_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveEvent_stmt(const event_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterGen_scope(const gen_scope* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveGen_scope(const gen_scope* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterRef_var(const ref_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveRef_var(const ref_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUdp_defn(const udp_defn* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUdp_defn(const udp_defn* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterNet_bit(const net_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveNet_bit(const net_bit* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDelay_term(const delay_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDelay_term(const delay_term* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSequence_inst(const sequence_inst* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSequence_inst(const sequence_inst* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterShort_int_typespec(const short_int_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveShort_int_typespec(const short_int_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTime_var(const time_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTime_var(const time_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterThread_obj(const thread_obj* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveThread_obj(const thread_obj* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInitial(const initial* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInitial(const initial* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterDo_while(const do_while* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveDo_while(const do_while* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterString_typespec(const string_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveString_typespec(const string_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterSys_task_call(const sys_task_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveSys_task_call(const sys_task_call* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterMod_path(const mod_path* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveMod_path(const mod_path* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterForeach_stmt(const foreach_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveForeach_stmt(const foreach_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterAssignment(const assignment* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveAssignment(const assignment* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterStruct_net(const struct_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveStruct_net(const struct_net* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterTime_typespec(const time_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveTime_typespec(const time_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterContinue_stmt(const continue_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveContinue_stmt(const continue_stmt* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterPacked_array_var(const packed_array_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leavePacked_array_var(const packed_array_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInstance_array(const instance_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInstance_array(const instance_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterReg_array(const reg_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveReg_array(const reg_array* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterBegin(const begin* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveBegin(const begin* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterInstance(const instance* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveInstance(const instance* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterExpr(const expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveExpr(const expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterReal_typespec(const real_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveReal_typespec(const real_typespec* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterUdp(const udp* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveUdp(const udp* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterLong_int_var(const long_int_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveLong_int_var(const long_int_var* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterClocking_block(const clocking_block* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveClocking_block(const clocking_block* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterConcurrent_assertions(const concurrent_assertions* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveConcurrent_assertions(const concurrent_assertions* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }

    virtual void enterMulticlock_sequence_expr(const multiclock_sequence_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }
    virtual void leaveMulticlock_sequence_expr(const multiclock_sequence_expr* object, const BaseClass* parent, vpiHandle handle, vpiHandle parentHandle) { }


};

}  // namespace UHDM


#endif
