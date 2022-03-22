#    Copyright (c) 2022
#    Author      : Bruno Capuano
#    Create Time : 2022 March
#    Change Log  :
#       – Read environmental variables
# 
#    The MIT License (MIT)
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.
import datetime
import os
from AzureIoTLogger import AzureIoTLogger

class AzureIoTEnvironment:
    @staticmethod
    def GetEnvVarString(name):
        varVal = os.environ[name]
        AzureIoTLogger.Log(f"Read Environment Var String '{name}': {varVal}")
        return varVal

    @staticmethod
    def GetEnvVarBool(name):
        varVal = bool(os.environ[name])
        AzureIoTLogger.Log(f"Read Environment Var Bool '{name}': {varVal}")
        return varVal        

    @staticmethod
    def GetEnvVarInt(name):
        varVal = int(os.environ[name])
        AzureIoTLogger.Log(f"Read Environment Var Int '{name}': {varVal}")
        return varVal        