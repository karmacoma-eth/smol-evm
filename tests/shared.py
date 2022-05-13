def with_stack_contents(context, some_iterable):
    for x in some_iterable:
        context.stack.push(x)
    return context
