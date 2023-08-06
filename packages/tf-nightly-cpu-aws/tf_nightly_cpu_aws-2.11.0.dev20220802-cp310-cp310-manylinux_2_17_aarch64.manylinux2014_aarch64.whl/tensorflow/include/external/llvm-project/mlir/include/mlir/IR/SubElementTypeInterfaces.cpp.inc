/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Definitions                                                      *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

void mlir::SubElementTypeInterface::walkImmediateSubElements(llvm::function_ref<void(mlir::Attribute)> walkAttrsFn, llvm::function_ref<void(mlir::Type)> walkTypesFn) const {
      return getImpl()->walkImmediateSubElements(getImpl(), *this, walkAttrsFn, walkTypesFn);
  }
::mlir::Type mlir::SubElementTypeInterface::replaceImmediateSubElements(::llvm::ArrayRef<::mlir::Attribute> replAttrs, ::llvm::ArrayRef<::mlir::Type> replTypes) const {
      return getImpl()->replaceImmediateSubElements(getImpl(), *this, replAttrs, replTypes);
  }
