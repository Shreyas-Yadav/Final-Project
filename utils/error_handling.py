import sys
from typing import Optional, Callable, Any

def handle_keyboard_interrupt(func: Callable) -> Callable:
    """Decorator to handle keyboard interrupts.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    return wrapper

def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """Safely execute a function and handle exceptions.
    
    Args:
        func: Function to execute
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Function result or None if execution fails
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Error: {e}")
        return None