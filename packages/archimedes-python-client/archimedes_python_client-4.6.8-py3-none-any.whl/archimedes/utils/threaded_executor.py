import sys
from concurrent.futures import ThreadPoolExecutor


def default_merge_function(result, aggr):
    """
    Default callback function for execute_many to merge the results

    Args:
        result: result of the execution
        aggr: aggregate to merge to

    Returns:
        Aggregated result
    """
    if aggr is None:
        aggr = []
    aggr.extend(result)
    return aggr


def execute_many(func, params_array, merge_function=default_merge_function):
    """
    Execute a function multiple times in parallel for params in params_array and merge
    the results using the merge_function.

    Args:
        func: function to execute
        params_array: array of parameters for the function
        merge_function: function to merge the result

    Returns:
        Aggregated result of multiple executions
    """
    aggr = None
    with ThreadPoolExecutor() as executor:
        try:
            futures = [
                executor.submit(
                    func,
                    **params,
                )
                for params in params_array
            ]

            for future in futures:
                aggr = merge_function(future.result(), aggr)
        except KeyboardInterrupt:
            print("Cancelling tasks")
            cancelled_count = 0
            total_count = 0
            running_count = 0
            for future in futures:
                total_count += 1
                if future.running():
                    running_count += 1
                if future.cancel():
                    cancelled_count += 1
            print(
                f"Cancelled {cancelled_count}/{total_count} tasks. "
                f"Waiting for {running_count} running tasks to complete..."
            )
            sys.exit()
    return aggr
