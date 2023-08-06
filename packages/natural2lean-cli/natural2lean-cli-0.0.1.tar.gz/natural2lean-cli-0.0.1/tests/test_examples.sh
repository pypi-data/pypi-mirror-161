#!/bin/bash

# Run this file from the root of the project
# `sh tests/test_examples.sh``

echo "\n---------------------"
echo "Testing main examples"
echo "---------------------"
for filename in tests/examples/*.tex; do
    echo "\n--- Testing $filename"
    natural2lean f $filename
done

echo "\n------------------"
echo "Testing variations"
echo "------------------"
for filename in tests/examples/variations/*.tex; do
    echo "\n--- Testing $filename"
    natural2lean f $filename
done

echo "\n----------------------------"
echo "Testing different approaches"
echo "----------------------------"
for filename in tests/examples/different-approaches-*/*.tex; do
    echo "\n--- Testing $filename"
    natural2lean f $filename
done