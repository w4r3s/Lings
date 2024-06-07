help:
    @echo "install - install dependencies"
    @echo "run - run the application"

# install dependencies
install:
    poetry install

# run the application
run:
    poetry run python lings/gui.py
