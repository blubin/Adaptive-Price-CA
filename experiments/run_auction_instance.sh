#!/bin/bash

# A script to run one instance from an experiment

source ./common.sh

program=adaptiveCA.run_auction_instance
python -m $program $@
