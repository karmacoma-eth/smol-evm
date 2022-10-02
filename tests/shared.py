from smol_evm.context import ExecutionContext, Calldata

def with_stack_contents(context, some_iterable) -> ExecutionContext:
    for x in some_iterable:
        context.stack.push(x)
    return context

def with_calldata(context, some_iterable) -> ExecutionContext:
    context.calldata = Calldata(bytes(some_iterable))
    return context

def with_memory(context, offset, some_iterable) -> ExecutionContext:
    for i, val in enumerate(some_iterable):
        context.memory.store(offset + i, val)
    return context
