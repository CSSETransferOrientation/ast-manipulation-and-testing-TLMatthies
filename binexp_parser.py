#!/usr/bin/python3
import os
from os.path import join as osjoin

import unittest

from enum import Enum

# Use these to distinguish node types, note that you might want to further
# distinguish between the addition and multiplication operators
NodeType = Enum('BinOpNodeType', ['number', 'operator'])

class BinOpAst():
    """
    A somewhat quick and dirty structure to represent a binary operator AST.

    Reads input as a list of tokens in prefix notation, converts into internal representation,
    then can convert to prefix, postfix, or infix string output.
    """
    def __init__(self, prefix_list):
        """
        Initialize a binary operator AST from a given list in prefix notation.
        Destroys the list that is passed in.
        """
        self.val = prefix_list.pop(0)
        if self.val.isnumeric():
            self.type = NodeType.number
            self.left = False
            self.right = False
        else:
            self.type = NodeType.operator
            self.left = BinOpAst(prefix_list)
            self.right = BinOpAst(prefix_list)

    def __str__(self, indent=0):
        """
        Convert the binary tree printable string where indentation level indicates
        parent/child relationships
        """
        ilvl = '  '*indent
        left = '\n  ' + ilvl + self.left.__str__(indent+1) if self.left else ''
        right = '\n  ' + ilvl + self.right.__str__(indent+1) if self.right else ''
        return f"{ilvl}{self.val}{left}{right}"

    def __repr__(self):
        """Generate the repr from the string"""
        return str(self)

    def prefix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.val + ' ' + self.left.prefix_str() + ' ' + self.right.prefix_str()

    def infix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return '(' + self.left.infix_str() + ' ' + self.val + ' ' + self.right.infix_str() + ')'
    def postfix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.left.postfix_str() + ' ' + self.right.postfix_str() + ' ' + self.val

    def additive_identity(self):
        """
        Reduce additive identities
        x + 0 = x
        """
        # Two base cases, can't do any work if we're on num, just return.
        if self.type == NodeType.number:
            return

        #call recursively on both children
        self.left.additive_identity()
        self.right.additive_identity()

        # ;;> It's much better to check if you are a '+' and then proceed. Imagine we add '/' or identifiers or something
        # ;;> It's going to be a pain to go through and update all of your code

        # sort of a different base case, can't do anything with mult (*), but still need to call recursively.
        if self.val == '*':
            return
        
        # If the left is a 0, then replace current val with right val. If both are 0, will be handled by parent.
        if self.left.val == '0':
            self.val = self.right.val
            self.type = self.right.type
            self.left = self.right.left
            self.right = self.right.right

        # Vice versa above.
        elif self.right.val == '0':
            self.val = self.left.val
            self.type = self.left.type
            self.right = self.left.right
            self.left = self.left.left

        # Nothing more to do, return.
        return


    def multiplicative_identity(self):
        """
        Reduce multiplicative identities
        x * 1 = x
        """
        # Two base cases, can't do any work if we're on num, just return.
        if self.type == NodeType.number:
            return

        #call recursively on both children
        self.left.multiplicative_identity()
        self.right.multiplicative_identity()

        # sort of a different base case, can't do anything with mult (*), but still need to call recursively.
        if self.val == '+':
            return
        
        # If the left is a 0, then replace current val with right val. If both are 0, will be handled by parent.
        if self.left.val == '1':
            self.val = self.right.val
            self.type = self.right.type
            self.left = self.right.left
            self.right = self.right.right

        # Vice versa above.
        elif self.right.val == '1':
            self.val = self.left.val
            self.type = self.left.type
            self.right = self.left.right
            self.left = self.left.left

        # Nothing more to do, return.
        return


    
    def mult_by_zero(self):
        """
        Reduce multiplication by zero
        x * 0 = 0
        """
        if self.type == NodeType.number:
            return

        self.left.mult_by_zero()
        self.right.mult_by_zero()

        if self.val == '+':
            return

        # Where is the bool coming from? There is never a bool assigned???? Let's go to sleep now.
        if self.left.val == '0':
            self.val = self.left.val
            self.type = self.left.type
            self.right = self.left.right
            self.left = self.left.left

        elif self.right.val == '0':
            self.val = self.right.val
            self.type = self.right.type
            self.left = self.right.left
            self.right = self.right.right

        return


    def constant_fold(self):
        """
        Fold constants,
        e.g. 1 + 2 = 3
        e.g. x + 2 = x + 2
        """
        # Optionally, IMPLEMENT ME! This is a bit more challenging. 
        # You also likely want to add an additional node type to your AST
        # to represent identifiers.
        pass            

    def simplify_binops(self):
        """
        Simplify binary trees with the following:
        1) Additive identity, e.g. x + 0 = x
        2) Multiplicative identity, e.g. x * 1 = x
        3) Extra #1: Multiplication by 0, e.g. x * 0 = 0
        4) Extra #2: Constant folding, e.g. statically we can reduce 1 + 1 to 2, but not x + 1 to anything
        """
        self.additive_identity()
        self.multiplicative_identity()
        self.mult_by_zero()
        self.constant_fold()

from os.path import join as osjoin
import os

class TreeOpTester(unittest.TestCase):
    def test_arith_id(self):
        print("\nTesting arith_id")
        # be able to work with directories
        input_files = osjoin('testbench/arith_id', 'inputs')
        output_files = osjoin('testbench/arith_id', 'outputs')
        log = []
        flag = True

        # iterate through sub files
        for file_name in os.listdir(input_files):
            # read in the input files
            current_file_inputs = open(osjoin(input_files, file_name))
            input_to_test = current_file_inputs.read().strip()
            current_file_inputs.close()

            # read in the output files
            current_file_outputs = open(osjoin(output_files, file_name))
            expected_output = current_file_outputs.read().strip()
            current_file_outputs.close()

            # build tree and run additive_identity()
            tree = BinOpAst(input_to_test.split())
            tree.additive_identity()
            actual_output = tree.prefix_str()

            # create a log of everything, this way we can run all tests, even if some fail.
            log.append((file_name, actual_output, expected_output))
            if actual_output != expected_output:
                flag = False

        # print out the log, then assert to see if any part of test failed.
        for item in log:
           print(f'{"!FAIL!" if item[1] != item[2] else "Passed"} {item[0]}: {item[1]} = {item[2]}')
        assert flag
        


    def test_mult_id(self):
        print("\nTesting mult_id")
        # be able to work with directories
        input_files = osjoin('testbench/mult_id', 'inputs')
        output_files = osjoin('testbench/mult_id', 'outputs')
        log = []
        flag = True

        # iterate through sub files
        for file_name in os.listdir(input_files):
            # read in the input files
            current_file_inputs = open(osjoin(input_files, file_name))
            input_to_test = current_file_inputs.read().strip()
            current_file_inputs.close()

            # read in the output files
            current_file_outputs = open(osjoin(output_files, file_name))
            expected_output = current_file_outputs.read().strip()
            current_file_outputs.close()

            # build tree and run multiplicitive_identity()
            tree = BinOpAst(input_to_test.split())
            tree.multiplicative_identity()
            actual_output = tree.prefix_str()

            # create a log of everything, this way we can run all tests, even if some fail.
            log.append((file_name, actual_output, expected_output))
            if actual_output != expected_output:
                flag = False

        # print out the log, then assert to see if any part of test failed.
        for item in log:
           print(f'{"!FAIL!" if item[1] != item[2] else "Passed"} {item[0]}: {item[1]} = {item[2]}')
        assert flag
 
    def test_mult_by_zero(self):
        print("\nTesting mult_by_zero")
        # be able to work with directories
        input_files = osjoin('testbench/mult_by_zero', 'inputs')
        output_files = osjoin('testbench/mult_by_zero', 'outputs')
        log = []
        flag = True

        # iterate through sub files
        for file_name in os.listdir(input_files):
            # read in the input files
            current_file_inputs = open(osjoin(input_files, file_name))
            input_to_test = current_file_inputs.read().strip()
            current_file_inputs.close()

            # read in the output files
            current_file_outputs = open(osjoin(output_files, file_name))
            expected_output = current_file_outputs.read().strip()
            current_file_outputs.close()

            # build tree and run additive_identity()
            tree = BinOpAst(input_to_test.split())
            tree.mult_by_zero()
            actual_output = tree.prefix_str()

            # create a log of everything, this way we can run all tests, even if some fail.
            log.append((file_name, actual_output, expected_output))
            if actual_output != expected_output:
                flag = False

        # print out the log, then assert to see if any part of test failed.
        for item in log:
           print(f'{"!FAIL!" if item[1] != item[2] else "Passed"} {item[0]}: {item[1]} = {item[2]}')
        assert flag
        



if __name__ == "__main__":
    unittest.main()
