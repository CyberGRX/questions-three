#!/bin/bash

if test -z "$PYPI_USER"; then
  echo '$PYPI_USER is empty'
  exit 1
fi

if test -z "$PYPI_PASS"; then
  echo '$PYPI_PASS is empty'
  exit 1
fi

if ! python3 -m twine upload -u $PYPI_USER -p $PYPI_PASS dist/*; then
  echo 'Deployment failed'
  exit 1
fi
