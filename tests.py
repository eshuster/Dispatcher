from solution import Q
import solution
import unittest
import json

def get_new_service():
    return solution.get_message_service()

def test_integer_negation():
    svc = get_new_service()
    svc.enqueue('{"test": "message", "int_value": 512}')
    returned = json.loads(svc.next(2))

    if returned["int_value"] != -513:
        print("**FAILED** You did not negate the integer value.")

def test_special_field():
    svc = get_new_service()
    svc.enqueue('{"test": "message", "_special": "This must go to queue 0"}')
    try:
        svc.next(0)
    except Exception:
        print("**FAILED** You did not send the special message to queue 0.")

_ = lambda x: json.loads(x)

class SolutionTest(unittest.TestCase):
    def setUp(self):
        self.q = Q()

    def test_integer_negation(self):
        test_integer_negation()


    def test_special_field(self):
        test_special_field()


    def test_sequence(self):
        q = self.q
        q.enqueue('{"_sequence": "A", "_part": 0, "test": "Hello"}')
        q.enqueue('{"_sequence": "A", "_part": 1, "test": "Hello"}')

        part_A_0 = q.next(3)
        part_A_1 = q.next(3)

        assert _(part_A_0) == {"_sequence": "A", "_part": 0, "test": "Hello"}, part_A_0
        assert _(part_A_1) == {"_sequence": "A", "_part": 1, "test": "Hello"}, part_A_1

    def test_sequence_and_hash(self):
        q = self.q
        q.enqueue('{"_sequence": "A", "_part": 0, "test": "World", "_hash": "test"}')
        q.enqueue('{"_sequence": "A", "_part": 1, "test": "World", "_hash": "test"}')
        q.enqueue('{"_sequence": "A", "_part": 2, "test": "World", "_hash": "test"}')
        q.enqueue('{"_sequence": "B", "_part": 0, "test": "World", "_hash": "test"}')

        part_A_0 = q.next(1)
        part_A_1 = q.next(1)
        part_A_2 = q.next(1)
        part_B_0 = q.next(1)

        assert _(part_A_0) == _('{"_sequence": "A", "_part": 0, "test": "World", "_hash": "test", "hash": "b\'eK5kfcVUTSJxMKBoKlHjC8d3f7ttio8XAHRjo+zR1SQ=\'"}'), (part_A_0, Q.encode('test'))
        assert _(part_A_1) == _('{"_sequence": "A", "_part": 1, "test": "World", "_hash": "test", "hash": "b\'eK5kfcVUTSJxMKBoKlHjC8d3f7ttio8XAHRjo+zR1SQ=\'"}'), (part_A_1, Q.encode('test'))   
        assert _(part_A_2) == _('{"_sequence": "A", "_part": 2, "test": "World", "_hash": "test", "hash": "b\'eK5kfcVUTSJxMKBoKlHjC8d3f7ttio8XAHRjo+zR1SQ=\'"}'), (part_A_2, Q.encode('test'))
        assert _(part_B_0) == _('{"_sequence": "B", "_part": 0, "test": "World", "_hash": "test", "hash": "b\'eK5kfcVUTSJxMKBoKlHjC8d3f7ttio8XAHRjo+zR1SQ=\'"}'), (part_B_0, Q.encode('test'))

    def test_hash(self):
        q = self.q
        q.enqueue('{"test": "World", "_hash": "test"}') 
        r = q.next(1)
        assert _(r) == _('{"test": "World", "_hash": "test", "hash": "b\'eK5kfcVUTSJxMKBoKlHjC8d3f7ttio8XAHRjo+zR1SQ=\'"}'), (r, Q.encode('test')) 

    def test_int(self):
        q = self.q
        q.enqueue('{"int_value" : 5}')
        r = q.next(2)
        assert r == '{"int_value": -6}'

    def test_hash_and_int(self):
        q = self.q
        q.enqueue('{"test": "World", "_hash": "test", "int_value": 5}') 
        r = q.next(1)
        assert _(r) == _('{"test": "World", "_hash": "test", "int_value": -6, "hash": "b\'eK5kfcVUTSJxMKBoKlHjC8d3f7ttio8XAHRjo+zR1SQ=\'"}'), (r, Q.encode('test'))

    def test_object_int_value(self):
        q = self.q
        q.enqueue('{"test": {"int_value": 5} }')
 
        r = q.next(2)  
        assert _(r) == _('{"test": {"int_value": -6} }')

    def test_object_double_int_value(self):
        q = self.q
        q.enqueue(json.dumps(dict(test=dict(inner_test=dict(int_value=5)))))
 
        r = q.next(2) 
       
        assert _(r) == dict(test=dict(inner_test=dict(int_value=-6))), r

if __name__ == '__main__':
    unittest.main()

