@echo off

if exist Scripts\activate.bat (
    call Scripts\activate  # Activate virtual environment if found
    echo Virtual environment activated.
) else (
    echo Virtual environment not found. Make sure 'myenv' exists in the current directory.
)

cmd  # Open command prompt
