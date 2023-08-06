import os
import subprocess

SQLCMD = '/opt/mssql-tools/bin/sqlcmd'
BCP = '/opt/mssql-tools/bin/bcp'

def check(executable, db):
    assert os.path.isfile(executable), f"File not found: {executable}"
    assert type(db) == dict, 'db argument must be a config dictionary.'
    assert 'Server' in db.keys(), 'db config dictionary must contain Server key.'
    assert 'User' in db.keys(), 'db config dictionary must contain User key.'
    assert 'Password' in db.keys(), 'db config dictionary must contain Password key.'
    assert 'Database' in db.keys(), 'db config dictionary must contain Database key.'

def bulkload(file, table, db, truncate_first = True, delete_first = False):
    global BCP
    check(BCP, db)

    res = ''
    if truncate_first:
        res = runquery("TRUNCATE TABLE {}".format(table))
    elif delete_first:
        res = runquery("DELETE FROM {}".format(table), db)
    try:
        res = subprocess.check_output([BCP, table, 'in', file,
                                       '-S', db['Server'], '-U', db['User'], '-P', db['Password'], '-d',
                                       db['Database'], '-c', '-e', '/dev/stdout', '-m', '0'])
    except subprocess.CalledProcessError as e:
        raise Exception('bcp returned exit code {}:\n{}'.format(e.returncode, e.output))
    return res

def runquery(sql, db):
    global SQLCMD
    check(SQLCMD, db)

    res = ''
    try:
        res = subprocess.check_output([SQLCMD, '-S', db['Server'],
                                       '-U', db['User'], '-P', db['Password'], '-d', db['Database'], '-Q', sql])
    except subprocess.CalledProcessError as e:
        raise Exception('sqlcmd returned exit code {}:\n{}'.format(e.returncode, e.output))
    return res

def runfile(path, db):
    global SQLCMD
    check(SQLCMD, db)

    res = ''
    try:
        res = subprocess.check_output([SQLCMD, '-S', db['Server'],
                                       '-U', db['User'], '-P', db['Password'], '-d', db['Database'], '-i', path])
    except subprocess.CalledProcessError as e:
        raise Exception('sqlcmd returned exit code {}:\n{}'.format(e.returncode, e.output))
    return res
