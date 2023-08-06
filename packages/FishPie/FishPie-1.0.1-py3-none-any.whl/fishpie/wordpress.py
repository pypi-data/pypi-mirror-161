# This file is part of Fishpie.
#
# Fishpie is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Fishpie is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fishpie.  If not, see <http://www.gnu.org/licenses/>.

import hashlib

import MySQLdb

def authenticate(user, password, db_host, db_user, db_passwd, db):
    """ Authenticate against a Wordpress database.
    """
    
    connection = MySQLdb.connect(db_host, db_user, db_passwd, db)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT user_pass FROM wp_users WHERE user_login = (%s)", (user,))
    entries = cursor.fetchall()
    if not entries:
        result = False
    else:
        stored_hash = entries[0][0]
        result = check_password(password, stored_hash)
    return result

itoa64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def encode64(input, count):
    """ Wordpress "base64" encoding.
    """
    
    output = ""
    i=0
    while i<count:
        value = input[i]
        i+=1
        output += itoa64[value&0x3f]
        if i<count:
            value |= input[i]<<8
        output += itoa64[(value >> 6)&0x3f]
        if i>=count:
            break
        i+=1
        if i<count:
            value |= input[i]<<16
        output += itoa64[(value >> 12)&0x3f]
        if i>= count:
            break
        i+=1
        output += itoa64[(value>>18)&0x3f]

    return output

def check_password(password, stored_hash):
    """ Replicate Wordpress password encryption.
    """
    
    if stored_hash[:3] != "$P$":
        raise Exception("Unknown password type: {0}".format(stored_hash[:3]))

    count_log2 = itoa64.index(stored_hash[3])
    count = 1<<count_log2

    salt = stored_hash[4:4+8].encode()

    password = password.encode("utf-8")
    data = hashlib.md5(salt+password).digest()
    for _ in range(count):
        data = hashlib.md5(data+password).digest()

    data = encode64(data, 16)
    return data==stored_hash[12:]
