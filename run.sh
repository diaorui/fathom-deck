#!/bin/bash
# Convenience script to run FathomDeck pipeline

export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
python -m fathom_deck "$@"
