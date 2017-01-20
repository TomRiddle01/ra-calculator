[![Build Status](https://travis-ci.org/TomRiddle01/spc-calculator.svg?branch=master)](https://travis-ci.org/TomRiddle01/ra-calculator)

# Introduction
This project was written for a university course about theoretic computer science.

~~It is written in Python and can evaluate SPC-Queries on a given database. SPC-queries are a subset of relational algebra where only σ (selection), π (projection) and x (cartesian product) are available.~~
The SPC-Version can now be found on an extra branch. The master branch will develop more features.

# Usage 
You can use `make shell` to start the database shell or you can just run the spcShell.py file with python3. 
The following usage is also valid.

    python3 spcShell.py <database file>
    python3 spcShell.py <database file> query


## Commands

    open <filename>     opens a database file
    tables              lists the loaded tables
    <spc-query>         a valid query will automatically be evaluated

## Examples

Instead of σ and and π you can use * for selection and # for projection.

    # all people and their living countrys
    % python spcShell.py example.txt '#1,7(*1=4(*6=5(People x Living x Places)))'
    Database loaded
    >>Query executed as π1,7(σ1=4(σ6=5(People x Living x Places)))
    ('Alfred', 'Germany')
    ('Superman', 'America')
    ('Jesus', 'Jerusalem')
    ('TomRiddle01', 'Germany')


    # all people from Hamburg
    % python spcShell.py example.txt '#1(*5="Hamburg"(*1=4(People x Living)))'
    Database loaded
    >>Query executed as π1(σ5="Hamburg"(σ1=4(People x Living)))
    ('Alfred',)
    ('TomRiddle01',)


# Test
To run the unittests use `make test`.

