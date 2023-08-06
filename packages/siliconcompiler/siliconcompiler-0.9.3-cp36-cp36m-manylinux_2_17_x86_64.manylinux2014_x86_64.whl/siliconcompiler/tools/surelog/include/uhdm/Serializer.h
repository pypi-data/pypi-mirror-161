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
 * File:   Serializer.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef SERIALIZER_UHDM_H
#define SERIALIZER_UHDM_H

#include <string>
#include <vector>
#include <map>

#include <iostream>
#include <functional>
#include <uhdm/uhdm.h>

namespace UHDM {
  enum ErrorType {
    UHDM_WRONG_OBJECT_TYPE = 703,
    UHDM_UNDEFINED_PATTERN_KEY = 712,
    UHDM_UNMATCHED_FIELD_IN_PATTERN_ASSIGN = 713
  };

  typedef std::function<void(ErrorType errType, const std::string&, any* object)> ErrorHandler;

  void DefaultErrorHandler(ErrorType errType, const std::string& errorMsg, any* object);

  template<typename T>
  class FactoryT;

  class Serializer {
  public:
    Serializer() : incrId_(0), objId_(0), errorHandler(DefaultErrorHandler) {symbolMaker.Make("");}
    void Save(const std::string& file);
    void Purge();
    void SetErrorHandler(ErrorHandler handler) { errorHandler = handler; }
    ErrorHandler GetErrorHandler() { return errorHandler; }
    const std::vector<vpiHandle> Restore(const std::string& file);
    std::map<std::string, unsigned long> ObjectStats() const;

  private:
    template<typename T, typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    T *Make(FactoryT<T> *const factory) {
      T* const obj = factory->Make();
      obj->SetSerializer(this);
      obj->UhdmId(objId_++);
      return obj;
    }

    template<typename T, typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    std::vector<T*>* Make(FactoryT<std::vector<T*>> *const factory) {
      return factory->Make();
    }

  public:
    attribute* MakeAttribute () { attribute* tmp = attributeMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<attribute*>* MakeAttributeVec () { return attributeVectMaker.Make();}
    virtual_interface_var* MakeVirtual_interface_var () { virtual_interface_var* tmp = virtual_interface_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<virtual_interface_var*>* MakeVirtual_interface_varVec () { return virtual_interface_varVectMaker.Make();}
    let_decl* MakeLet_decl () { let_decl* tmp = let_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<let_decl*>* MakeLet_declVec () { return let_declVectMaker.Make();}
    std::vector<concurrent_assertions*>* MakeConcurrent_assertionsVec () { return concurrent_assertionsVectMaker.Make();}
    std::vector<process_stmt*>* MakeProcess_stmtVec () { return process_stmtVectMaker.Make();}
    always* MakeAlways () { always* tmp = alwaysMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<always*>* MakeAlwaysVec () { return alwaysVectMaker.Make();}
    final_stmt* MakeFinal_stmt () { final_stmt* tmp = final_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<final_stmt*>* MakeFinal_stmtVec () { return final_stmtVectMaker.Make();}
    initial* MakeInitial () { initial* tmp = initialMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<initial*>* MakeInitialVec () { return initialVectMaker.Make();}
    std::vector<atomic_stmt*>* MakeAtomic_stmtVec () { return atomic_stmtVectMaker.Make();}
    delay_control* MakeDelay_control () { delay_control* tmp = delay_controlMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<delay_control*>* MakeDelay_controlVec () { return delay_controlVectMaker.Make();}
    delay_term* MakeDelay_term () { delay_term* tmp = delay_termMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<delay_term*>* MakeDelay_termVec () { return delay_termVectMaker.Make();}
    event_control* MakeEvent_control () { event_control* tmp = event_controlMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<event_control*>* MakeEvent_controlVec () { return event_controlVectMaker.Make();}
    repeat_control* MakeRepeat_control () { repeat_control* tmp = repeat_controlMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<repeat_control*>* MakeRepeat_controlVec () { return repeat_controlVectMaker.Make();}
    std::vector<scope*>* MakeScopeVec () { return scopeVectMaker.Make();}
    begin* MakeBegin () { begin* tmp = beginMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<begin*>* MakeBeginVec () { return beginVectMaker.Make();}
    named_begin* MakeNamed_begin () { named_begin* tmp = named_beginMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<named_begin*>* MakeNamed_beginVec () { return named_beginVectMaker.Make();}
    named_fork* MakeNamed_fork () { named_fork* tmp = named_forkMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<named_fork*>* MakeNamed_forkVec () { return named_forkVectMaker.Make();}
    fork_stmt* MakeFork_stmt () { fork_stmt* tmp = fork_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<fork_stmt*>* MakeFork_stmtVec () { return fork_stmtVectMaker.Make();}
    for_stmt* MakeFor_stmt () { for_stmt* tmp = for_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<for_stmt*>* MakeFor_stmtVec () { return for_stmtVectMaker.Make();}
    if_stmt* MakeIf_stmt () { if_stmt* tmp = if_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<if_stmt*>* MakeIf_stmtVec () { return if_stmtVectMaker.Make();}
    event_stmt* MakeEvent_stmt () { event_stmt* tmp = event_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<event_stmt*>* MakeEvent_stmtVec () { return event_stmtVectMaker.Make();}
    thread_obj* MakeThread_obj () { thread_obj* tmp = thread_objMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<thread_obj*>* MakeThread_objVec () { return thread_objVectMaker.Make();}
    forever_stmt* MakeForever_stmt () { forever_stmt* tmp = forever_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<forever_stmt*>* MakeForever_stmtVec () { return forever_stmtVectMaker.Make();}
    std::vector<waits*>* MakeWaitsVec () { return waitsVectMaker.Make();}
    wait_stmt* MakeWait_stmt () { wait_stmt* tmp = wait_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<wait_stmt*>* MakeWait_stmtVec () { return wait_stmtVectMaker.Make();}
    wait_fork* MakeWait_fork () { wait_fork* tmp = wait_forkMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<wait_fork*>* MakeWait_forkVec () { return wait_forkVectMaker.Make();}
    ordered_wait* MakeOrdered_wait () { ordered_wait* tmp = ordered_waitMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<ordered_wait*>* MakeOrdered_waitVec () { return ordered_waitVectMaker.Make();}
    std::vector<disables*>* MakeDisablesVec () { return disablesVectMaker.Make();}
    disable* MakeDisable () { disable* tmp = disableMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<disable*>* MakeDisableVec () { return disableVectMaker.Make();}
    disable_fork* MakeDisable_fork () { disable_fork* tmp = disable_forkMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<disable_fork*>* MakeDisable_forkVec () { return disable_forkVectMaker.Make();}
    continue_stmt* MakeContinue_stmt () { continue_stmt* tmp = continue_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<continue_stmt*>* MakeContinue_stmtVec () { return continue_stmtVectMaker.Make();}
    break_stmt* MakeBreak_stmt () { break_stmt* tmp = break_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<break_stmt*>* MakeBreak_stmtVec () { return break_stmtVectMaker.Make();}
    return_stmt* MakeReturn_stmt () { return_stmt* tmp = return_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<return_stmt*>* MakeReturn_stmtVec () { return return_stmtVectMaker.Make();}
    while_stmt* MakeWhile_stmt () { while_stmt* tmp = while_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<while_stmt*>* MakeWhile_stmtVec () { return while_stmtVectMaker.Make();}
    repeat* MakeRepeat () { repeat* tmp = repeatMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<repeat*>* MakeRepeatVec () { return repeatVectMaker.Make();}
    do_while* MakeDo_while () { do_while* tmp = do_whileMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<do_while*>* MakeDo_whileVec () { return do_whileVectMaker.Make();}
    if_else* MakeIf_else () { if_else* tmp = if_elseMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<if_else*>* MakeIf_elseVec () { return if_elseVectMaker.Make();}
    case_stmt* MakeCase_stmt () { case_stmt* tmp = case_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<case_stmt*>* MakeCase_stmtVec () { return case_stmtVectMaker.Make();}
    force* MakeForce () { force* tmp = forceMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<force*>* MakeForceVec () { return forceVectMaker.Make();}
    assign_stmt* MakeAssign_stmt () { assign_stmt* tmp = assign_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<assign_stmt*>* MakeAssign_stmtVec () { return assign_stmtVectMaker.Make();}
    deassign* MakeDeassign () { deassign* tmp = deassignMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<deassign*>* MakeDeassignVec () { return deassignVectMaker.Make();}
    release* MakeRelease () { release* tmp = releaseMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<release*>* MakeReleaseVec () { return releaseVectMaker.Make();}
    null_stmt* MakeNull_stmt () { null_stmt* tmp = null_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<null_stmt*>* MakeNull_stmtVec () { return null_stmtVectMaker.Make();}
    expect_stmt* MakeExpect_stmt () { expect_stmt* tmp = expect_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<expect_stmt*>* MakeExpect_stmtVec () { return expect_stmtVectMaker.Make();}
    foreach_stmt* MakeForeach_stmt () { foreach_stmt* tmp = foreach_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<foreach_stmt*>* MakeForeach_stmtVec () { return foreach_stmtVectMaker.Make();}
    gen_scope* MakeGen_scope () { gen_scope* tmp = gen_scopeMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<gen_scope*>* MakeGen_scopeVec () { return gen_scopeVectMaker.Make();}
    gen_var* MakeGen_var () { gen_var* tmp = gen_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<gen_var*>* MakeGen_varVec () { return gen_varVectMaker.Make();}
    gen_scope_array* MakeGen_scope_array () { gen_scope_array* tmp = gen_scope_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<gen_scope_array*>* MakeGen_scope_arrayVec () { return gen_scope_arrayVectMaker.Make();}
    assert_stmt* MakeAssert_stmt () { assert_stmt* tmp = assert_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<assert_stmt*>* MakeAssert_stmtVec () { return assert_stmtVectMaker.Make();}
    cover* MakeCover () { cover* tmp = coverMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<cover*>* MakeCoverVec () { return coverVectMaker.Make();}
    assume* MakeAssume () { assume* tmp = assumeMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<assume*>* MakeAssumeVec () { return assumeVectMaker.Make();}
    restrict* MakeRestrict () { restrict* tmp = restrictMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<restrict*>* MakeRestrictVec () { return restrictVectMaker.Make();}
    immediate_assert* MakeImmediate_assert () { immediate_assert* tmp = immediate_assertMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<immediate_assert*>* MakeImmediate_assertVec () { return immediate_assertVectMaker.Make();}
    immediate_assume* MakeImmediate_assume () { immediate_assume* tmp = immediate_assumeMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<immediate_assume*>* MakeImmediate_assumeVec () { return immediate_assumeVectMaker.Make();}
    immediate_cover* MakeImmediate_cover () { immediate_cover* tmp = immediate_coverMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<immediate_cover*>* MakeImmediate_coverVec () { return immediate_coverVectMaker.Make();}
    std::vector<expr*>* MakeExprVec () { return exprVectMaker.Make();}
    case_item* MakeCase_item () { case_item* tmp = case_itemMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<case_item*>* MakeCase_itemVec () { return case_itemVectMaker.Make();}
    assignment* MakeAssignment () { assignment* tmp = assignmentMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<assignment*>* MakeAssignmentVec () { return assignmentVectMaker.Make();}
    any_pattern* MakeAny_pattern () { any_pattern* tmp = any_patternMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<any_pattern*>* MakeAny_patternVec () { return any_patternVectMaker.Make();}
    tagged_pattern* MakeTagged_pattern () { tagged_pattern* tmp = tagged_patternMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<tagged_pattern*>* MakeTagged_patternVec () { return tagged_patternVectMaker.Make();}
    struct_pattern* MakeStruct_pattern () { struct_pattern* tmp = struct_patternMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<struct_pattern*>* MakeStruct_patternVec () { return struct_patternVectMaker.Make();}
    unsupported_expr* MakeUnsupported_expr () { unsupported_expr* tmp = unsupported_exprMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<unsupported_expr*>* MakeUnsupported_exprVec () { return unsupported_exprVectMaker.Make();}
    unsupported_stmt* MakeUnsupported_stmt () { unsupported_stmt* tmp = unsupported_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<unsupported_stmt*>* MakeUnsupported_stmtVec () { return unsupported_stmtVectMaker.Make();}
    sequence_inst* MakeSequence_inst () { sequence_inst* tmp = sequence_instMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<sequence_inst*>* MakeSequence_instVec () { return sequence_instVectMaker.Make();}
    seq_formal_decl* MakeSeq_formal_decl () { seq_formal_decl* tmp = seq_formal_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<seq_formal_decl*>* MakeSeq_formal_declVec () { return seq_formal_declVectMaker.Make();}
    sequence_decl* MakeSequence_decl () { sequence_decl* tmp = sequence_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<sequence_decl*>* MakeSequence_declVec () { return sequence_declVectMaker.Make();}
    prop_formal_decl* MakeProp_formal_decl () { prop_formal_decl* tmp = prop_formal_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<prop_formal_decl*>* MakeProp_formal_declVec () { return prop_formal_declVectMaker.Make();}
    property_inst* MakeProperty_inst () { property_inst* tmp = property_instMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<property_inst*>* MakeProperty_instVec () { return property_instVectMaker.Make();}
    property_spec* MakeProperty_spec () { property_spec* tmp = property_specMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<property_spec*>* MakeProperty_specVec () { return property_specVectMaker.Make();}
    property_decl* MakeProperty_decl () { property_decl* tmp = property_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<property_decl*>* MakeProperty_declVec () { return property_declVectMaker.Make();}
    clocked_property* MakeClocked_property () { clocked_property* tmp = clocked_propertyMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<clocked_property*>* MakeClocked_propertyVec () { return clocked_propertyVectMaker.Make();}
    case_property_item* MakeCase_property_item () { case_property_item* tmp = case_property_itemMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<case_property_item*>* MakeCase_property_itemVec () { return case_property_itemVectMaker.Make();}
    case_property* MakeCase_property () { case_property* tmp = case_propertyMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<case_property*>* MakeCase_propertyVec () { return case_propertyVectMaker.Make();}
    multiclock_sequence_expr* MakeMulticlock_sequence_expr () { multiclock_sequence_expr* tmp = multiclock_sequence_exprMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<multiclock_sequence_expr*>* MakeMulticlock_sequence_exprVec () { return multiclock_sequence_exprVectMaker.Make();}
    clocked_seq* MakeClocked_seq () { clocked_seq* tmp = clocked_seqMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<clocked_seq*>* MakeClocked_seqVec () { return clocked_seqVectMaker.Make();}
    std::vector<simple_expr*>* MakeSimple_exprVec () { return simple_exprVectMaker.Make();}
    constant* MakeConstant () { constant* tmp = constantMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<constant*>* MakeConstantVec () { return constantVectMaker.Make();}
    let_expr* MakeLet_expr () { let_expr* tmp = let_exprMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<let_expr*>* MakeLet_exprVec () { return let_exprVectMaker.Make();}
    operation* MakeOperation () { operation* tmp = operationMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<operation*>* MakeOperationVec () { return operationVectMaker.Make();}
    part_select* MakePart_select () { part_select* tmp = part_selectMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<part_select*>* MakePart_selectVec () { return part_selectVectMaker.Make();}
    indexed_part_select* MakeIndexed_part_select () { indexed_part_select* tmp = indexed_part_selectMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<indexed_part_select*>* MakeIndexed_part_selectVec () { return indexed_part_selectVectMaker.Make();}
    ref_obj* MakeRef_obj () { ref_obj* tmp = ref_objMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<ref_obj*>* MakeRef_objVec () { return ref_objVectMaker.Make();}
    hier_path* MakeHier_path () { hier_path* tmp = hier_pathMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<hier_path*>* MakeHier_pathVec () { return hier_pathVectMaker.Make();}
    var_select* MakeVar_select () { var_select* tmp = var_selectMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<var_select*>* MakeVar_selectVec () { return var_selectVectMaker.Make();}
    bit_select* MakeBit_select () { bit_select* tmp = bit_selectMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<bit_select*>* MakeBit_selectVec () { return bit_selectVectMaker.Make();}
    std::vector<variables*>* MakeVariablesVec () { return variablesVectMaker.Make();}
    ref_var* MakeRef_var () { ref_var* tmp = ref_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<ref_var*>* MakeRef_varVec () { return ref_varVectMaker.Make();}
    short_real_var* MakeShort_real_var () { short_real_var* tmp = short_real_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<short_real_var*>* MakeShort_real_varVec () { return short_real_varVectMaker.Make();}
    real_var* MakeReal_var () { real_var* tmp = real_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<real_var*>* MakeReal_varVec () { return real_varVectMaker.Make();}
    byte_var* MakeByte_var () { byte_var* tmp = byte_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<byte_var*>* MakeByte_varVec () { return byte_varVectMaker.Make();}
    short_int_var* MakeShort_int_var () { short_int_var* tmp = short_int_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<short_int_var*>* MakeShort_int_varVec () { return short_int_varVectMaker.Make();}
    int_var* MakeInt_var () { int_var* tmp = int_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<int_var*>* MakeInt_varVec () { return int_varVectMaker.Make();}
    long_int_var* MakeLong_int_var () { long_int_var* tmp = long_int_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<long_int_var*>* MakeLong_int_varVec () { return long_int_varVectMaker.Make();}
    integer_var* MakeInteger_var () { integer_var* tmp = integer_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<integer_var*>* MakeInteger_varVec () { return integer_varVectMaker.Make();}
    time_var* MakeTime_var () { time_var* tmp = time_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<time_var*>* MakeTime_varVec () { return time_varVectMaker.Make();}
    array_var* MakeArray_var () { array_var* tmp = array_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<array_var*>* MakeArray_varVec () { return array_varVectMaker.Make();}
    reg_array* MakeReg_array () { reg_array* tmp = reg_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<reg_array*>* MakeReg_arrayVec () { return reg_arrayVectMaker.Make();}
    reg* MakeReg () { reg* tmp = regMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<reg*>* MakeRegVec () { return regVectMaker.Make();}
    packed_array_var* MakePacked_array_var () { packed_array_var* tmp = packed_array_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<packed_array_var*>* MakePacked_array_varVec () { return packed_array_varVectMaker.Make();}
    bit_var* MakeBit_var () { bit_var* tmp = bit_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<bit_var*>* MakeBit_varVec () { return bit_varVectMaker.Make();}
    logic_var* MakeLogic_var () { logic_var* tmp = logic_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<logic_var*>* MakeLogic_varVec () { return logic_varVectMaker.Make();}
    struct_var* MakeStruct_var () { struct_var* tmp = struct_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<struct_var*>* MakeStruct_varVec () { return struct_varVectMaker.Make();}
    union_var* MakeUnion_var () { union_var* tmp = union_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<union_var*>* MakeUnion_varVec () { return union_varVectMaker.Make();}
    enum_var* MakeEnum_var () { enum_var* tmp = enum_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<enum_var*>* MakeEnum_varVec () { return enum_varVectMaker.Make();}
    string_var* MakeString_var () { string_var* tmp = string_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<string_var*>* MakeString_varVec () { return string_varVectMaker.Make();}
    chandle_var* MakeChandle_var () { chandle_var* tmp = chandle_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<chandle_var*>* MakeChandle_varVec () { return chandle_varVectMaker.Make();}
    var_bit* MakeVar_bit () { var_bit* tmp = var_bitMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<var_bit*>* MakeVar_bitVec () { return var_bitVectMaker.Make();}
    std::vector<task_func*>* MakeTask_funcVec () { return task_funcVectMaker.Make();}
    task* MakeTask () { task* tmp = taskMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<task*>* MakeTaskVec () { return taskVectMaker.Make();}
    function* MakeFunction () { function* tmp = functionMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<function*>* MakeFunctionVec () { return functionVectMaker.Make();}
    modport* MakeModport () { modport* tmp = modportMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<modport*>* MakeModportVec () { return modportVectMaker.Make();}
    interface_tf_decl* MakeInterface_tf_decl () { interface_tf_decl* tmp = interface_tf_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<interface_tf_decl*>* MakeInterface_tf_declVec () { return interface_tf_declVectMaker.Make();}
    cont_assign* MakeCont_assign () { cont_assign* tmp = cont_assignMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<cont_assign*>* MakeCont_assignVec () { return cont_assignVectMaker.Make();}
    cont_assign_bit* MakeCont_assign_bit () { cont_assign_bit* tmp = cont_assign_bitMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<cont_assign_bit*>* MakeCont_assign_bitVec () { return cont_assign_bitVectMaker.Make();}
    std::vector<ports*>* MakePortsVec () { return portsVectMaker.Make();}
    port* MakePort () { port* tmp = portMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<port*>* MakePortVec () { return portVectMaker.Make();}
    port_bit* MakePort_bit () { port_bit* tmp = port_bitMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<port_bit*>* MakePort_bitVec () { return port_bitVectMaker.Make();}
    std::vector<primitive*>* MakePrimitiveVec () { return primitiveVectMaker.Make();}
    gate* MakeGate () { gate* tmp = gateMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<gate*>* MakeGateVec () { return gateVectMaker.Make();}
    switch_tran* MakeSwitch_tran () { switch_tran* tmp = switch_tranMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<switch_tran*>* MakeSwitch_tranVec () { return switch_tranVectMaker.Make();}
    udp* MakeUdp () { udp* tmp = udpMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<udp*>* MakeUdpVec () { return udpVectMaker.Make();}
    mod_path* MakeMod_path () { mod_path* tmp = mod_pathMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<mod_path*>* MakeMod_pathVec () { return mod_pathVectMaker.Make();}
    tchk* MakeTchk () { tchk* tmp = tchkMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<tchk*>* MakeTchkVec () { return tchkVectMaker.Make();}
    range* MakeRange () { range* tmp = rangeMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<range*>* MakeRangeVec () { return rangeVectMaker.Make();}
    udp_defn* MakeUdp_defn () { udp_defn* tmp = udp_defnMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<udp_defn*>* MakeUdp_defnVec () { return udp_defnVectMaker.Make();}
    table_entry* MakeTable_entry () { table_entry* tmp = table_entryMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<table_entry*>* MakeTable_entryVec () { return table_entryVectMaker.Make();}
    io_decl* MakeIo_decl () { io_decl* tmp = io_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<io_decl*>* MakeIo_declVec () { return io_declVectMaker.Make();}
    alias_stmt* MakeAlias_stmt () { alias_stmt* tmp = alias_stmtMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<alias_stmt*>* MakeAlias_stmtVec () { return alias_stmtVectMaker.Make();}
    clocking_block* MakeClocking_block () { clocking_block* tmp = clocking_blockMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<clocking_block*>* MakeClocking_blockVec () { return clocking_blockVectMaker.Make();}
    clocking_io_decl* MakeClocking_io_decl () { clocking_io_decl* tmp = clocking_io_declMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<clocking_io_decl*>* MakeClocking_io_declVec () { return clocking_io_declVectMaker.Make();}
    param_assign* MakeParam_assign () { param_assign* tmp = param_assignMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<param_assign*>* MakeParam_assignVec () { return param_assignVectMaker.Make();}
    std::vector<instance_array*>* MakeInstance_arrayVec () { return instance_arrayVectMaker.Make();}
    interface_array* MakeInterface_array () { interface_array* tmp = interface_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<interface_array*>* MakeInterface_arrayVec () { return interface_arrayVectMaker.Make();}
    program_array* MakeProgram_array () { program_array* tmp = program_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<program_array*>* MakeProgram_arrayVec () { return program_arrayVectMaker.Make();}
    module_array* MakeModule_array () { module_array* tmp = module_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<module_array*>* MakeModule_arrayVec () { return module_arrayVectMaker.Make();}
    std::vector<primitive_array*>* MakePrimitive_arrayVec () { return primitive_arrayVectMaker.Make();}
    gate_array* MakeGate_array () { gate_array* tmp = gate_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<gate_array*>* MakeGate_arrayVec () { return gate_arrayVectMaker.Make();}
    switch_array* MakeSwitch_array () { switch_array* tmp = switch_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<switch_array*>* MakeSwitch_arrayVec () { return switch_arrayVectMaker.Make();}
    udp_array* MakeUdp_array () { udp_array* tmp = udp_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<udp_array*>* MakeUdp_arrayVec () { return udp_arrayVectMaker.Make();}
    std::vector<typespec*>* MakeTypespecVec () { return typespecVectMaker.Make();}
    std::vector<net_drivers*>* MakeNet_driversVec () { return net_driversVectMaker.Make();}
    std::vector<net_loads*>* MakeNet_loadsVec () { return net_loadsVectMaker.Make();}
    prim_term* MakePrim_term () { prim_term* tmp = prim_termMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<prim_term*>* MakePrim_termVec () { return prim_termVectMaker.Make();}
    path_term* MakePath_term () { path_term* tmp = path_termMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<path_term*>* MakePath_termVec () { return path_termVectMaker.Make();}
    tchk_term* MakeTchk_term () { tchk_term* tmp = tchk_termMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<tchk_term*>* MakeTchk_termVec () { return tchk_termVectMaker.Make();}
    std::vector<nets*>* MakeNetsVec () { return netsVectMaker.Make();}
    net_bit* MakeNet_bit () { net_bit* tmp = net_bitMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<net_bit*>* MakeNet_bitVec () { return net_bitVectMaker.Make();}
    std::vector<net*>* MakeNetVec () { return netVectMaker.Make();}
    struct_net* MakeStruct_net () { struct_net* tmp = struct_netMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<struct_net*>* MakeStruct_netVec () { return struct_netVectMaker.Make();}
    enum_net* MakeEnum_net () { enum_net* tmp = enum_netMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<enum_net*>* MakeEnum_netVec () { return enum_netVectMaker.Make();}
    integer_net* MakeInteger_net () { integer_net* tmp = integer_netMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<integer_net*>* MakeInteger_netVec () { return integer_netVectMaker.Make();}
    time_net* MakeTime_net () { time_net* tmp = time_netMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<time_net*>* MakeTime_netVec () { return time_netVectMaker.Make();}
    logic_net* MakeLogic_net () { logic_net* tmp = logic_netMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<logic_net*>* MakeLogic_netVec () { return logic_netVectMaker.Make();}
    array_net* MakeArray_net () { array_net* tmp = array_netMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<array_net*>* MakeArray_netVec () { return array_netVectMaker.Make();}
    packed_array_net* MakePacked_array_net () { packed_array_net* tmp = packed_array_netMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<packed_array_net*>* MakePacked_array_netVec () { return packed_array_netVectMaker.Make();}
    event_typespec* MakeEvent_typespec () { event_typespec* tmp = event_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<event_typespec*>* MakeEvent_typespecVec () { return event_typespecVectMaker.Make();}
    named_event* MakeNamed_event () { named_event* tmp = named_eventMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<named_event*>* MakeNamed_eventVec () { return named_eventVectMaker.Make();}
    named_event_array* MakeNamed_event_array () { named_event_array* tmp = named_event_arrayMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<named_event_array*>* MakeNamed_event_arrayVec () { return named_event_arrayVectMaker.Make();}
    parameter* MakeParameter () { parameter* tmp = parameterMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<parameter*>* MakeParameterVec () { return parameterVectMaker.Make();}
    def_param* MakeDef_param () { def_param* tmp = def_paramMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<def_param*>* MakeDef_paramVec () { return def_paramVectMaker.Make();}
    spec_param* MakeSpec_param () { spec_param* tmp = spec_paramMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<spec_param*>* MakeSpec_paramVec () { return spec_paramVectMaker.Make();}
    class_typespec* MakeClass_typespec () { class_typespec* tmp = class_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<class_typespec*>* MakeClass_typespecVec () { return class_typespecVectMaker.Make();}
    extends* MakeExtends () { extends* tmp = extendsMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<extends*>* MakeExtendsVec () { return extendsVectMaker.Make();}
    class_defn* MakeClass_defn () { class_defn* tmp = class_defnMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<class_defn*>* MakeClass_defnVec () { return class_defnVectMaker.Make();}
    class_obj* MakeClass_obj () { class_obj* tmp = class_objMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<class_obj*>* MakeClass_objVec () { return class_objVectMaker.Make();}
    class_var* MakeClass_var () { class_var* tmp = class_varMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<class_var*>* MakeClass_varVec () { return class_varVectMaker.Make();}
    std::vector<instance*>* MakeInstanceVec () { return instanceVectMaker.Make();}
    interface* MakeInterface () { interface* tmp = interfaceMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<interface*>* MakeInterfaceVec () { return interfaceVectMaker.Make();}
    program* MakeProgram () { program* tmp = programMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<program*>* MakeProgramVec () { return programVectMaker.Make();}
    package* MakePackage () { package* tmp = packageMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<package*>* MakePackageVec () { return packageVectMaker.Make();}
    module* MakeModule () { module* tmp = moduleMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<module*>* MakeModuleVec () { return moduleVectMaker.Make();}
    short_real_typespec* MakeShort_real_typespec () { short_real_typespec* tmp = short_real_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<short_real_typespec*>* MakeShort_real_typespecVec () { return short_real_typespecVectMaker.Make();}
    real_typespec* MakeReal_typespec () { real_typespec* tmp = real_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<real_typespec*>* MakeReal_typespecVec () { return real_typespecVectMaker.Make();}
    byte_typespec* MakeByte_typespec () { byte_typespec* tmp = byte_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<byte_typespec*>* MakeByte_typespecVec () { return byte_typespecVectMaker.Make();}
    short_int_typespec* MakeShort_int_typespec () { short_int_typespec* tmp = short_int_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<short_int_typespec*>* MakeShort_int_typespecVec () { return short_int_typespecVectMaker.Make();}
    int_typespec* MakeInt_typespec () { int_typespec* tmp = int_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<int_typespec*>* MakeInt_typespecVec () { return int_typespecVectMaker.Make();}
    long_int_typespec* MakeLong_int_typespec () { long_int_typespec* tmp = long_int_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<long_int_typespec*>* MakeLong_int_typespecVec () { return long_int_typespecVectMaker.Make();}
    integer_typespec* MakeInteger_typespec () { integer_typespec* tmp = integer_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<integer_typespec*>* MakeInteger_typespecVec () { return integer_typespecVectMaker.Make();}
    time_typespec* MakeTime_typespec () { time_typespec* tmp = time_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<time_typespec*>* MakeTime_typespecVec () { return time_typespecVectMaker.Make();}
    enum_typespec* MakeEnum_typespec () { enum_typespec* tmp = enum_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<enum_typespec*>* MakeEnum_typespecVec () { return enum_typespecVectMaker.Make();}
    string_typespec* MakeString_typespec () { string_typespec* tmp = string_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<string_typespec*>* MakeString_typespecVec () { return string_typespecVectMaker.Make();}
    chandle_typespec* MakeChandle_typespec () { chandle_typespec* tmp = chandle_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<chandle_typespec*>* MakeChandle_typespecVec () { return chandle_typespecVectMaker.Make();}
    struct_typespec* MakeStruct_typespec () { struct_typespec* tmp = struct_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<struct_typespec*>* MakeStruct_typespecVec () { return struct_typespecVectMaker.Make();}
    union_typespec* MakeUnion_typespec () { union_typespec* tmp = union_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<union_typespec*>* MakeUnion_typespecVec () { return union_typespecVectMaker.Make();}
    logic_typespec* MakeLogic_typespec () { logic_typespec* tmp = logic_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<logic_typespec*>* MakeLogic_typespecVec () { return logic_typespecVectMaker.Make();}
    packed_array_typespec* MakePacked_array_typespec () { packed_array_typespec* tmp = packed_array_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<packed_array_typespec*>* MakePacked_array_typespecVec () { return packed_array_typespecVectMaker.Make();}
    array_typespec* MakeArray_typespec () { array_typespec* tmp = array_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<array_typespec*>* MakeArray_typespecVec () { return array_typespecVectMaker.Make();}
    void_typespec* MakeVoid_typespec () { void_typespec* tmp = void_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<void_typespec*>* MakeVoid_typespecVec () { return void_typespecVectMaker.Make();}
    unsupported_typespec* MakeUnsupported_typespec () { unsupported_typespec* tmp = unsupported_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<unsupported_typespec*>* MakeUnsupported_typespecVec () { return unsupported_typespecVectMaker.Make();}
    sequence_typespec* MakeSequence_typespec () { sequence_typespec* tmp = sequence_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<sequence_typespec*>* MakeSequence_typespecVec () { return sequence_typespecVectMaker.Make();}
    property_typespec* MakeProperty_typespec () { property_typespec* tmp = property_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<property_typespec*>* MakeProperty_typespecVec () { return property_typespecVectMaker.Make();}
    interface_typespec* MakeInterface_typespec () { interface_typespec* tmp = interface_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<interface_typespec*>* MakeInterface_typespecVec () { return interface_typespecVectMaker.Make();}
    type_parameter* MakeType_parameter () { type_parameter* tmp = type_parameterMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<type_parameter*>* MakeType_parameterVec () { return type_parameterVectMaker.Make();}
    typespec_member* MakeTypespec_member () { typespec_member* tmp = typespec_memberMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<typespec_member*>* MakeTypespec_memberVec () { return typespec_memberVectMaker.Make();}
    enum_const* MakeEnum_const () { enum_const* tmp = enum_constMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<enum_const*>* MakeEnum_constVec () { return enum_constVectMaker.Make();}
    bit_typespec* MakeBit_typespec () { bit_typespec* tmp = bit_typespecMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<bit_typespec*>* MakeBit_typespecVec () { return bit_typespecVectMaker.Make();}
    std::vector<tf_call*>* MakeTf_callVec () { return tf_callVectMaker.Make();}
    user_systf* MakeUser_systf () { user_systf* tmp = user_systfMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<user_systf*>* MakeUser_systfVec () { return user_systfVectMaker.Make();}
    sys_func_call* MakeSys_func_call () { sys_func_call* tmp = sys_func_callMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<sys_func_call*>* MakeSys_func_callVec () { return sys_func_callVectMaker.Make();}
    sys_task_call* MakeSys_task_call () { sys_task_call* tmp = sys_task_callMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<sys_task_call*>* MakeSys_task_callVec () { return sys_task_callVectMaker.Make();}
    method_func_call* MakeMethod_func_call () { method_func_call* tmp = method_func_callMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<method_func_call*>* MakeMethod_func_callVec () { return method_func_callVectMaker.Make();}
    method_task_call* MakeMethod_task_call () { method_task_call* tmp = method_task_callMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<method_task_call*>* MakeMethod_task_callVec () { return method_task_callVectMaker.Make();}
    func_call* MakeFunc_call () { func_call* tmp = func_callMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<func_call*>* MakeFunc_callVec () { return func_callVectMaker.Make();}
    task_call* MakeTask_call () { task_call* tmp = task_callMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<task_call*>* MakeTask_callVec () { return task_callVectMaker.Make();}
    std::vector<constraint_expr*>* MakeConstraint_exprVec () { return constraint_exprVectMaker.Make();}
    constraint_ordering* MakeConstraint_ordering () { constraint_ordering* tmp = constraint_orderingMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<constraint_ordering*>* MakeConstraint_orderingVec () { return constraint_orderingVectMaker.Make();}
    constraint* MakeConstraint () { constraint* tmp = constraintMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<constraint*>* MakeConstraintVec () { return constraintVectMaker.Make();}
    import* MakeImport () { import* tmp = importMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<import*>* MakeImportVec () { return importVectMaker.Make();}
    dist_item* MakeDist_item () { dist_item* tmp = dist_itemMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<dist_item*>* MakeDist_itemVec () { return dist_itemVectMaker.Make();}
    distribution* MakeDistribution () { distribution* tmp = distributionMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<distribution*>* MakeDistributionVec () { return distributionVectMaker.Make();}
    implication* MakeImplication () { implication* tmp = implicationMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<implication*>* MakeImplicationVec () { return implicationVectMaker.Make();}
    constr_if* MakeConstr_if () { constr_if* tmp = constr_ifMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<constr_if*>* MakeConstr_ifVec () { return constr_ifVectMaker.Make();}
    constr_if_else* MakeConstr_if_else () { constr_if_else* tmp = constr_if_elseMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<constr_if_else*>* MakeConstr_if_elseVec () { return constr_if_elseVectMaker.Make();}
    constr_foreach* MakeConstr_foreach () { constr_foreach* tmp = constr_foreachMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<constr_foreach*>* MakeConstr_foreachVec () { return constr_foreachVectMaker.Make();}
    soft_disable* MakeSoft_disable () { soft_disable* tmp = soft_disableMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<soft_disable*>* MakeSoft_disableVec () { return soft_disableVectMaker.Make();}
    design* MakeDesign () { design* tmp = designMaker.Make(); tmp->SetSerializer(this); tmp->UhdmId(objId_++); return tmp;}
    std::vector<design*>* MakeDesignVec () { return designVectMaker.Make();}

    std::vector<any*>* MakeAnyVec() { return anyVectMaker.Make(); }
    vpiHandle MakeUhdmHandle(UHDM_OBJECT_TYPE type, const void* object) { return uhdm_handleMaker.Make(type, object); }

    VectorOfanyFactory anyVectMaker;
    SymbolFactory symbolMaker;
    uhdm_handleFactory uhdm_handleMaker;
    attributeFactory attributeMaker;
    VectorOfattributeFactory attributeVectMaker;
    virtual_interface_varFactory virtual_interface_varMaker;
    VectorOfvirtual_interface_varFactory virtual_interface_varVectMaker;
    let_declFactory let_declMaker;
    VectorOflet_declFactory let_declVectMaker;
    VectorOfconcurrent_assertionsFactory concurrent_assertionsVectMaker;
    VectorOfprocess_stmtFactory process_stmtVectMaker;
    alwaysFactory alwaysMaker;
    VectorOfalwaysFactory alwaysVectMaker;
    final_stmtFactory final_stmtMaker;
    VectorOffinal_stmtFactory final_stmtVectMaker;
    initialFactory initialMaker;
    VectorOfinitialFactory initialVectMaker;
    VectorOfatomic_stmtFactory atomic_stmtVectMaker;
    delay_controlFactory delay_controlMaker;
    VectorOfdelay_controlFactory delay_controlVectMaker;
    delay_termFactory delay_termMaker;
    VectorOfdelay_termFactory delay_termVectMaker;
    event_controlFactory event_controlMaker;
    VectorOfevent_controlFactory event_controlVectMaker;
    repeat_controlFactory repeat_controlMaker;
    VectorOfrepeat_controlFactory repeat_controlVectMaker;
    VectorOfscopeFactory scopeVectMaker;
    beginFactory beginMaker;
    VectorOfbeginFactory beginVectMaker;
    named_beginFactory named_beginMaker;
    VectorOfnamed_beginFactory named_beginVectMaker;
    named_forkFactory named_forkMaker;
    VectorOfnamed_forkFactory named_forkVectMaker;
    fork_stmtFactory fork_stmtMaker;
    VectorOffork_stmtFactory fork_stmtVectMaker;
    for_stmtFactory for_stmtMaker;
    VectorOffor_stmtFactory for_stmtVectMaker;
    if_stmtFactory if_stmtMaker;
    VectorOfif_stmtFactory if_stmtVectMaker;
    event_stmtFactory event_stmtMaker;
    VectorOfevent_stmtFactory event_stmtVectMaker;
    thread_objFactory thread_objMaker;
    VectorOfthread_objFactory thread_objVectMaker;
    forever_stmtFactory forever_stmtMaker;
    VectorOfforever_stmtFactory forever_stmtVectMaker;
    VectorOfwaitsFactory waitsVectMaker;
    wait_stmtFactory wait_stmtMaker;
    VectorOfwait_stmtFactory wait_stmtVectMaker;
    wait_forkFactory wait_forkMaker;
    VectorOfwait_forkFactory wait_forkVectMaker;
    ordered_waitFactory ordered_waitMaker;
    VectorOfordered_waitFactory ordered_waitVectMaker;
    VectorOfdisablesFactory disablesVectMaker;
    disableFactory disableMaker;
    VectorOfdisableFactory disableVectMaker;
    disable_forkFactory disable_forkMaker;
    VectorOfdisable_forkFactory disable_forkVectMaker;
    continue_stmtFactory continue_stmtMaker;
    VectorOfcontinue_stmtFactory continue_stmtVectMaker;
    break_stmtFactory break_stmtMaker;
    VectorOfbreak_stmtFactory break_stmtVectMaker;
    return_stmtFactory return_stmtMaker;
    VectorOfreturn_stmtFactory return_stmtVectMaker;
    while_stmtFactory while_stmtMaker;
    VectorOfwhile_stmtFactory while_stmtVectMaker;
    repeatFactory repeatMaker;
    VectorOfrepeatFactory repeatVectMaker;
    do_whileFactory do_whileMaker;
    VectorOfdo_whileFactory do_whileVectMaker;
    if_elseFactory if_elseMaker;
    VectorOfif_elseFactory if_elseVectMaker;
    case_stmtFactory case_stmtMaker;
    VectorOfcase_stmtFactory case_stmtVectMaker;
    forceFactory forceMaker;
    VectorOfforceFactory forceVectMaker;
    assign_stmtFactory assign_stmtMaker;
    VectorOfassign_stmtFactory assign_stmtVectMaker;
    deassignFactory deassignMaker;
    VectorOfdeassignFactory deassignVectMaker;
    releaseFactory releaseMaker;
    VectorOfreleaseFactory releaseVectMaker;
    null_stmtFactory null_stmtMaker;
    VectorOfnull_stmtFactory null_stmtVectMaker;
    expect_stmtFactory expect_stmtMaker;
    VectorOfexpect_stmtFactory expect_stmtVectMaker;
    foreach_stmtFactory foreach_stmtMaker;
    VectorOfforeach_stmtFactory foreach_stmtVectMaker;
    gen_scopeFactory gen_scopeMaker;
    VectorOfgen_scopeFactory gen_scopeVectMaker;
    gen_varFactory gen_varMaker;
    VectorOfgen_varFactory gen_varVectMaker;
    gen_scope_arrayFactory gen_scope_arrayMaker;
    VectorOfgen_scope_arrayFactory gen_scope_arrayVectMaker;
    assert_stmtFactory assert_stmtMaker;
    VectorOfassert_stmtFactory assert_stmtVectMaker;
    coverFactory coverMaker;
    VectorOfcoverFactory coverVectMaker;
    assumeFactory assumeMaker;
    VectorOfassumeFactory assumeVectMaker;
    restrictFactory restrictMaker;
    VectorOfrestrictFactory restrictVectMaker;
    immediate_assertFactory immediate_assertMaker;
    VectorOfimmediate_assertFactory immediate_assertVectMaker;
    immediate_assumeFactory immediate_assumeMaker;
    VectorOfimmediate_assumeFactory immediate_assumeVectMaker;
    immediate_coverFactory immediate_coverMaker;
    VectorOfimmediate_coverFactory immediate_coverVectMaker;
    VectorOfexprFactory exprVectMaker;
    case_itemFactory case_itemMaker;
    VectorOfcase_itemFactory case_itemVectMaker;
    assignmentFactory assignmentMaker;
    VectorOfassignmentFactory assignmentVectMaker;
    any_patternFactory any_patternMaker;
    VectorOfany_patternFactory any_patternVectMaker;
    tagged_patternFactory tagged_patternMaker;
    VectorOftagged_patternFactory tagged_patternVectMaker;
    struct_patternFactory struct_patternMaker;
    VectorOfstruct_patternFactory struct_patternVectMaker;
    unsupported_exprFactory unsupported_exprMaker;
    VectorOfunsupported_exprFactory unsupported_exprVectMaker;
    unsupported_stmtFactory unsupported_stmtMaker;
    VectorOfunsupported_stmtFactory unsupported_stmtVectMaker;
    sequence_instFactory sequence_instMaker;
    VectorOfsequence_instFactory sequence_instVectMaker;
    seq_formal_declFactory seq_formal_declMaker;
    VectorOfseq_formal_declFactory seq_formal_declVectMaker;
    sequence_declFactory sequence_declMaker;
    VectorOfsequence_declFactory sequence_declVectMaker;
    prop_formal_declFactory prop_formal_declMaker;
    VectorOfprop_formal_declFactory prop_formal_declVectMaker;
    property_instFactory property_instMaker;
    VectorOfproperty_instFactory property_instVectMaker;
    property_specFactory property_specMaker;
    VectorOfproperty_specFactory property_specVectMaker;
    property_declFactory property_declMaker;
    VectorOfproperty_declFactory property_declVectMaker;
    clocked_propertyFactory clocked_propertyMaker;
    VectorOfclocked_propertyFactory clocked_propertyVectMaker;
    case_property_itemFactory case_property_itemMaker;
    VectorOfcase_property_itemFactory case_property_itemVectMaker;
    case_propertyFactory case_propertyMaker;
    VectorOfcase_propertyFactory case_propertyVectMaker;
    multiclock_sequence_exprFactory multiclock_sequence_exprMaker;
    VectorOfmulticlock_sequence_exprFactory multiclock_sequence_exprVectMaker;
    clocked_seqFactory clocked_seqMaker;
    VectorOfclocked_seqFactory clocked_seqVectMaker;
    VectorOfsimple_exprFactory simple_exprVectMaker;
    constantFactory constantMaker;
    VectorOfconstantFactory constantVectMaker;
    let_exprFactory let_exprMaker;
    VectorOflet_exprFactory let_exprVectMaker;
    operationFactory operationMaker;
    VectorOfoperationFactory operationVectMaker;
    part_selectFactory part_selectMaker;
    VectorOfpart_selectFactory part_selectVectMaker;
    indexed_part_selectFactory indexed_part_selectMaker;
    VectorOfindexed_part_selectFactory indexed_part_selectVectMaker;
    ref_objFactory ref_objMaker;
    VectorOfref_objFactory ref_objVectMaker;
    hier_pathFactory hier_pathMaker;
    VectorOfhier_pathFactory hier_pathVectMaker;
    var_selectFactory var_selectMaker;
    VectorOfvar_selectFactory var_selectVectMaker;
    bit_selectFactory bit_selectMaker;
    VectorOfbit_selectFactory bit_selectVectMaker;
    VectorOfvariablesFactory variablesVectMaker;
    ref_varFactory ref_varMaker;
    VectorOfref_varFactory ref_varVectMaker;
    short_real_varFactory short_real_varMaker;
    VectorOfshort_real_varFactory short_real_varVectMaker;
    real_varFactory real_varMaker;
    VectorOfreal_varFactory real_varVectMaker;
    byte_varFactory byte_varMaker;
    VectorOfbyte_varFactory byte_varVectMaker;
    short_int_varFactory short_int_varMaker;
    VectorOfshort_int_varFactory short_int_varVectMaker;
    int_varFactory int_varMaker;
    VectorOfint_varFactory int_varVectMaker;
    long_int_varFactory long_int_varMaker;
    VectorOflong_int_varFactory long_int_varVectMaker;
    integer_varFactory integer_varMaker;
    VectorOfinteger_varFactory integer_varVectMaker;
    time_varFactory time_varMaker;
    VectorOftime_varFactory time_varVectMaker;
    array_varFactory array_varMaker;
    VectorOfarray_varFactory array_varVectMaker;
    reg_arrayFactory reg_arrayMaker;
    VectorOfreg_arrayFactory reg_arrayVectMaker;
    regFactory regMaker;
    VectorOfregFactory regVectMaker;
    packed_array_varFactory packed_array_varMaker;
    VectorOfpacked_array_varFactory packed_array_varVectMaker;
    bit_varFactory bit_varMaker;
    VectorOfbit_varFactory bit_varVectMaker;
    logic_varFactory logic_varMaker;
    VectorOflogic_varFactory logic_varVectMaker;
    struct_varFactory struct_varMaker;
    VectorOfstruct_varFactory struct_varVectMaker;
    union_varFactory union_varMaker;
    VectorOfunion_varFactory union_varVectMaker;
    enum_varFactory enum_varMaker;
    VectorOfenum_varFactory enum_varVectMaker;
    string_varFactory string_varMaker;
    VectorOfstring_varFactory string_varVectMaker;
    chandle_varFactory chandle_varMaker;
    VectorOfchandle_varFactory chandle_varVectMaker;
    var_bitFactory var_bitMaker;
    VectorOfvar_bitFactory var_bitVectMaker;
    VectorOftask_funcFactory task_funcVectMaker;
    taskFactory taskMaker;
    VectorOftaskFactory taskVectMaker;
    functionFactory functionMaker;
    VectorOffunctionFactory functionVectMaker;
    modportFactory modportMaker;
    VectorOfmodportFactory modportVectMaker;
    interface_tf_declFactory interface_tf_declMaker;
    VectorOfinterface_tf_declFactory interface_tf_declVectMaker;
    cont_assignFactory cont_assignMaker;
    VectorOfcont_assignFactory cont_assignVectMaker;
    cont_assign_bitFactory cont_assign_bitMaker;
    VectorOfcont_assign_bitFactory cont_assign_bitVectMaker;
    VectorOfportsFactory portsVectMaker;
    portFactory portMaker;
    VectorOfportFactory portVectMaker;
    port_bitFactory port_bitMaker;
    VectorOfport_bitFactory port_bitVectMaker;
    VectorOfprimitiveFactory primitiveVectMaker;
    gateFactory gateMaker;
    VectorOfgateFactory gateVectMaker;
    switch_tranFactory switch_tranMaker;
    VectorOfswitch_tranFactory switch_tranVectMaker;
    udpFactory udpMaker;
    VectorOfudpFactory udpVectMaker;
    mod_pathFactory mod_pathMaker;
    VectorOfmod_pathFactory mod_pathVectMaker;
    tchkFactory tchkMaker;
    VectorOftchkFactory tchkVectMaker;
    rangeFactory rangeMaker;
    VectorOfrangeFactory rangeVectMaker;
    udp_defnFactory udp_defnMaker;
    VectorOfudp_defnFactory udp_defnVectMaker;
    table_entryFactory table_entryMaker;
    VectorOftable_entryFactory table_entryVectMaker;
    io_declFactory io_declMaker;
    VectorOfio_declFactory io_declVectMaker;
    alias_stmtFactory alias_stmtMaker;
    VectorOfalias_stmtFactory alias_stmtVectMaker;
    clocking_blockFactory clocking_blockMaker;
    VectorOfclocking_blockFactory clocking_blockVectMaker;
    clocking_io_declFactory clocking_io_declMaker;
    VectorOfclocking_io_declFactory clocking_io_declVectMaker;
    param_assignFactory param_assignMaker;
    VectorOfparam_assignFactory param_assignVectMaker;
    VectorOfinstance_arrayFactory instance_arrayVectMaker;
    interface_arrayFactory interface_arrayMaker;
    VectorOfinterface_arrayFactory interface_arrayVectMaker;
    program_arrayFactory program_arrayMaker;
    VectorOfprogram_arrayFactory program_arrayVectMaker;
    module_arrayFactory module_arrayMaker;
    VectorOfmodule_arrayFactory module_arrayVectMaker;
    VectorOfprimitive_arrayFactory primitive_arrayVectMaker;
    gate_arrayFactory gate_arrayMaker;
    VectorOfgate_arrayFactory gate_arrayVectMaker;
    switch_arrayFactory switch_arrayMaker;
    VectorOfswitch_arrayFactory switch_arrayVectMaker;
    udp_arrayFactory udp_arrayMaker;
    VectorOfudp_arrayFactory udp_arrayVectMaker;
    VectorOftypespecFactory typespecVectMaker;
    VectorOfnet_driversFactory net_driversVectMaker;
    VectorOfnet_loadsFactory net_loadsVectMaker;
    prim_termFactory prim_termMaker;
    VectorOfprim_termFactory prim_termVectMaker;
    path_termFactory path_termMaker;
    VectorOfpath_termFactory path_termVectMaker;
    tchk_termFactory tchk_termMaker;
    VectorOftchk_termFactory tchk_termVectMaker;
    VectorOfnetsFactory netsVectMaker;
    net_bitFactory net_bitMaker;
    VectorOfnet_bitFactory net_bitVectMaker;
    VectorOfnetFactory netVectMaker;
    struct_netFactory struct_netMaker;
    VectorOfstruct_netFactory struct_netVectMaker;
    enum_netFactory enum_netMaker;
    VectorOfenum_netFactory enum_netVectMaker;
    integer_netFactory integer_netMaker;
    VectorOfinteger_netFactory integer_netVectMaker;
    time_netFactory time_netMaker;
    VectorOftime_netFactory time_netVectMaker;
    logic_netFactory logic_netMaker;
    VectorOflogic_netFactory logic_netVectMaker;
    array_netFactory array_netMaker;
    VectorOfarray_netFactory array_netVectMaker;
    packed_array_netFactory packed_array_netMaker;
    VectorOfpacked_array_netFactory packed_array_netVectMaker;
    event_typespecFactory event_typespecMaker;
    VectorOfevent_typespecFactory event_typespecVectMaker;
    named_eventFactory named_eventMaker;
    VectorOfnamed_eventFactory named_eventVectMaker;
    named_event_arrayFactory named_event_arrayMaker;
    VectorOfnamed_event_arrayFactory named_event_arrayVectMaker;
    parameterFactory parameterMaker;
    VectorOfparameterFactory parameterVectMaker;
    def_paramFactory def_paramMaker;
    VectorOfdef_paramFactory def_paramVectMaker;
    spec_paramFactory spec_paramMaker;
    VectorOfspec_paramFactory spec_paramVectMaker;
    class_typespecFactory class_typespecMaker;
    VectorOfclass_typespecFactory class_typespecVectMaker;
    extendsFactory extendsMaker;
    VectorOfextendsFactory extendsVectMaker;
    class_defnFactory class_defnMaker;
    VectorOfclass_defnFactory class_defnVectMaker;
    class_objFactory class_objMaker;
    VectorOfclass_objFactory class_objVectMaker;
    class_varFactory class_varMaker;
    VectorOfclass_varFactory class_varVectMaker;
    VectorOfinstanceFactory instanceVectMaker;
    interfaceFactory interfaceMaker;
    VectorOfinterfaceFactory interfaceVectMaker;
    programFactory programMaker;
    VectorOfprogramFactory programVectMaker;
    packageFactory packageMaker;
    VectorOfpackageFactory packageVectMaker;
    moduleFactory moduleMaker;
    VectorOfmoduleFactory moduleVectMaker;
    short_real_typespecFactory short_real_typespecMaker;
    VectorOfshort_real_typespecFactory short_real_typespecVectMaker;
    real_typespecFactory real_typespecMaker;
    VectorOfreal_typespecFactory real_typespecVectMaker;
    byte_typespecFactory byte_typespecMaker;
    VectorOfbyte_typespecFactory byte_typespecVectMaker;
    short_int_typespecFactory short_int_typespecMaker;
    VectorOfshort_int_typespecFactory short_int_typespecVectMaker;
    int_typespecFactory int_typespecMaker;
    VectorOfint_typespecFactory int_typespecVectMaker;
    long_int_typespecFactory long_int_typespecMaker;
    VectorOflong_int_typespecFactory long_int_typespecVectMaker;
    integer_typespecFactory integer_typespecMaker;
    VectorOfinteger_typespecFactory integer_typespecVectMaker;
    time_typespecFactory time_typespecMaker;
    VectorOftime_typespecFactory time_typespecVectMaker;
    enum_typespecFactory enum_typespecMaker;
    VectorOfenum_typespecFactory enum_typespecVectMaker;
    string_typespecFactory string_typespecMaker;
    VectorOfstring_typespecFactory string_typespecVectMaker;
    chandle_typespecFactory chandle_typespecMaker;
    VectorOfchandle_typespecFactory chandle_typespecVectMaker;
    struct_typespecFactory struct_typespecMaker;
    VectorOfstruct_typespecFactory struct_typespecVectMaker;
    union_typespecFactory union_typespecMaker;
    VectorOfunion_typespecFactory union_typespecVectMaker;
    logic_typespecFactory logic_typespecMaker;
    VectorOflogic_typespecFactory logic_typespecVectMaker;
    packed_array_typespecFactory packed_array_typespecMaker;
    VectorOfpacked_array_typespecFactory packed_array_typespecVectMaker;
    array_typespecFactory array_typespecMaker;
    VectorOfarray_typespecFactory array_typespecVectMaker;
    void_typespecFactory void_typespecMaker;
    VectorOfvoid_typespecFactory void_typespecVectMaker;
    unsupported_typespecFactory unsupported_typespecMaker;
    VectorOfunsupported_typespecFactory unsupported_typespecVectMaker;
    sequence_typespecFactory sequence_typespecMaker;
    VectorOfsequence_typespecFactory sequence_typespecVectMaker;
    property_typespecFactory property_typespecMaker;
    VectorOfproperty_typespecFactory property_typespecVectMaker;
    interface_typespecFactory interface_typespecMaker;
    VectorOfinterface_typespecFactory interface_typespecVectMaker;
    type_parameterFactory type_parameterMaker;
    VectorOftype_parameterFactory type_parameterVectMaker;
    typespec_memberFactory typespec_memberMaker;
    VectorOftypespec_memberFactory typespec_memberVectMaker;
    enum_constFactory enum_constMaker;
    VectorOfenum_constFactory enum_constVectMaker;
    bit_typespecFactory bit_typespecMaker;
    VectorOfbit_typespecFactory bit_typespecVectMaker;
    VectorOftf_callFactory tf_callVectMaker;
    user_systfFactory user_systfMaker;
    VectorOfuser_systfFactory user_systfVectMaker;
    sys_func_callFactory sys_func_callMaker;
    VectorOfsys_func_callFactory sys_func_callVectMaker;
    sys_task_callFactory sys_task_callMaker;
    VectorOfsys_task_callFactory sys_task_callVectMaker;
    method_func_callFactory method_func_callMaker;
    VectorOfmethod_func_callFactory method_func_callVectMaker;
    method_task_callFactory method_task_callMaker;
    VectorOfmethod_task_callFactory method_task_callVectMaker;
    func_callFactory func_callMaker;
    VectorOffunc_callFactory func_callVectMaker;
    task_callFactory task_callMaker;
    VectorOftask_callFactory task_callVectMaker;
    VectorOfconstraint_exprFactory constraint_exprVectMaker;
    constraint_orderingFactory constraint_orderingMaker;
    VectorOfconstraint_orderingFactory constraint_orderingVectMaker;
    constraintFactory constraintMaker;
    VectorOfconstraintFactory constraintVectMaker;
    importFactory importMaker;
    VectorOfimportFactory importVectMaker;
    dist_itemFactory dist_itemMaker;
    VectorOfdist_itemFactory dist_itemVectMaker;
    distributionFactory distributionMaker;
    VectorOfdistributionFactory distributionVectMaker;
    implicationFactory implicationMaker;
    VectorOfimplicationFactory implicationVectMaker;
    constr_ifFactory constr_ifMaker;
    VectorOfconstr_ifFactory constr_ifVectMaker;
    constr_if_elseFactory constr_if_elseMaker;
    VectorOfconstr_if_elseFactory constr_if_elseVectMaker;
    constr_foreachFactory constr_foreachMaker;
    VectorOfconstr_foreachFactory constr_foreachVectMaker;
    soft_disableFactory soft_disableMaker;
    VectorOfsoft_disableFactory soft_disableVectMaker;
    designFactory designMaker;
    VectorOfdesignFactory designVectMaker;


    std::unordered_map<const BaseClass*, unsigned long>& AllObjects() { return allIds_; }

  private:
    template<typename T, typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    void SetSaveId_(FactoryT<T>* const factory);

    template<typename T, typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    void SetRestoreId_(FactoryT<T>* const factory, unsigned long count);

    template<
      typename T, typename U,
      typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    struct AnySaveAdapter {};
    template<typename, typename, typename> friend struct AnySaveAdapter;

    template<
      typename T, typename U,
      typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    struct VectorOfanySaveAdapter {};
    template<typename, typename, typename> friend struct VectorOfanySaveAdapter;

    template<
      typename T, typename U,
      typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    struct AnyRestoreAdapter {};
    template<typename, typename, typename> friend struct AnyRestoreAdapter;

    template<
      typename T, typename U,
      typename = typename std::enable_if<std::is_base_of<BaseClass, T>::value>::type>
    struct VectorOfanyRestoreAdapter {};
    template<typename, typename, typename> friend struct VectorOfanyRestoreAdapter;

  private:
    BaseClass* GetObject(unsigned int objectType, unsigned int index);
    void SetId(const BaseClass* p, unsigned long id);
    unsigned long GetId(const BaseClass* p) ;
    std::unordered_map<const BaseClass*, unsigned long> allIds_;
    unsigned long incrId_; // Capnp id
    unsigned long objId_;  // ID for property annotations

    ErrorHandler errorHandler;
  };
};

#endif
