# Advanced OS Assignment 1

This repository contains my implementation for Task 3 of the Advanced Operating Systems assignment.

## Structure

t3/
- task3.py
- submission_log.txt
- test.txt
- test.pdf
- test.docx
- big.pdf

## Description

The program simulates login attempts and records system activity in a log file.

It handles:
- login success and failure
- repeated login detection
- alert generation
- file submission tracking

## How to run

Make sure Python 3 is installed.

Run:

python3 t3/task3.py

## Notes

- submission_log.txt stores all logs
- test files are used for simulation
- large files are included only for testing


## Example Output

The system logs login attempts in the following format:

timestamp - event - user.

Example:
1774230297 - LOGIN FAILED - user1
1774230297 - ALERT - Repeated login for user1

## Author

alidev8
