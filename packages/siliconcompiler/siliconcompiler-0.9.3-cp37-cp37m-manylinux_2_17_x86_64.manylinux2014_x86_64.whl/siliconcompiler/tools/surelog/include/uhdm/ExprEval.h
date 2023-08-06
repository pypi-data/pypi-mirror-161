// -*- c++ -*-

/*

 Copyright 2019-2021 Alain Dargelas

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
 * File:   ExprEval.h
 * Author: alaindargelas
 *
 * Created on July 3, 2021, 8:03 PM
 */

#ifndef UHDM_EXPREVAL_H
#define UHDM_EXPREVAL_H

#include <uhdm/typespec.h>
#include <uhdm/expr.h>
#include <iostream>
#include <sstream>

namespace UHDM {
  class Serializer;
  class ExprEval {
 
  public:
    
    bool isFullySpecified(const typespec* tps);

    expr* flattenPatternAssignments(Serializer& s, const typespec* tps, expr* assignExpr);

    void prettyPrint(Serializer& s, const any* tree, uint32_t indent, std::ostream &out);

    std::string prettyPrint(UHDM::any* handle);
  };
  
  std::string vPrint(UHDM::any* handle);

}

#endif
