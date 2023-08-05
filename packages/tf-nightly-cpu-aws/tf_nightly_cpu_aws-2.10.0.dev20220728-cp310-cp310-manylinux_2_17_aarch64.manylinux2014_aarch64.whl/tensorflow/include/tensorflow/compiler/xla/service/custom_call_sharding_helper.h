/* Copyright 2022 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#include "tensorflow/compiler/xla/service/hlo_instruction.h"
#include "tensorflow/compiler/xla/service/hlo_sharding.h"

#ifndef TENSORFLOW_COMPILER_XLA_SERVICE_CUSTOM_CALL_SHARDING_HELPER_H_
#define TENSORFLOW_COMPILER_XLA_SERVICE_CUSTOM_CALL_SHARDING_HELPER_H_

namespace xla {

// Helper class that helps implement sharding propagation policies for
// CustomCalls. It is called and used by the ShardingPropagation pass. Meant to
// be overridden by targets.
class CustomCallShardingHelper {
 public:
  // Function that manipulates an instruction sharding based on a user wanting
  // to update the sharding of an instruction.
  virtual HloSharding PropagateUserSharding(const HloInstruction* instruction,
                                            const HloInstruction* user,
                                            const HloSharding& sharding) const;
  // Infer sharding from the operands of an instruction.
  virtual std::optional<HloSharding> InferShardingFromOperands(
      const HloInstruction* instruction) const;
  // Returns if the instruction passed as parameter is a supported custom-call
  // for which the functions of this class are implemented.
  virtual bool IsCustomCallShardable(const HloInstruction* instruction) const;
  virtual ~CustomCallShardingHelper() = default;
};

}  // namespace xla

#endif  // TENSORFLOW_COMPILER_XLA_SERVICE_CUSTOM_CALL_SHARDING_HELPER_H__
