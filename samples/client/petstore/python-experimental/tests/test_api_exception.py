# coding: utf-8

# flake8: noqa

"""
Run the tests.
$ pip install nose (optional)
$ cd petstore_api-python
$ nosetests -v
"""

import os
import sys
import unittest

import petstore_api

from .util import id_gen

class ApiExceptionTests(unittest.TestCase):

    def setUp(self):
        self.api_client = petstore_api.ApiClient()
        from petstore_api.api.pet_api import PetApi
        self.pet_api = PetApi(self.api_client)
        self.setUpModels()

    def setUpModels(self):
        from petstore_api.model import category, tag, pet
        self.category = category.Category()
        self.category.id = id_gen()
        self.category.name = "dog"
        self.tag = tag.Tag()
        self.tag.id = id_gen()
        self.tag.full_name = "blank"
        self.pet = pet.Pet(name="hello kity", photo_urls=["http://foo.bar.com/1", "http://foo.bar.com/2"])
        self.pet.id = id_gen()
        self.pet.status = "sold"
        self.pet.category = self.category
        self.pet.tags = [self.tag]

    def test_404_error(self):
        self.pet_api.add_pet(self.pet)
        self.pet_api.delete_pet(pet_id=self.pet.id)

        with self.checkRaiseRegex(petstore_api.ApiException, "Pet not found"):
            self.pet_api.get_pet_by_id(pet_id=self.pet.id)

        try:
            self.pet_api.get_pet_by_id(pet_id=self.pet.id)
        except petstore_api.ApiException as e:
            self.assertEqual(e.status, 404)
            self.assertEqual(e.reason, "Not Found")
            self.checkRegex(e.body, "Pet not found")

    def test_500_error(self):
        self.pet_api.add_pet(self.pet)

        with self.checkRaiseRegex(petstore_api.ApiException, "Internal Server Error"):
            self.pet_api.upload_file(
                pet_id=self.pet.id,
                additional_metadata="special"
            )

        try:
            self.pet_api.upload_file(
                pet_id=self.pet.id,
                additional_metadata="special"
            )
        except petstore_api.ApiException as e:
            self.assertEqual(e.status, 500)
            self.assertEqual(e.reason, "Internal Server Error")
            self.checkRegex(e.body, "Error 500 Internal Server Error")

    def checkRaiseRegex(self, expected_exception, expected_regex):
        if sys.version_info < (3, 0):
            return self.assertRaisesRegexp(expected_exception, expected_regex)

        return self.assertRaisesRegex(expected_exception, expected_regex)

    def checkRegex(self, text, expected_regex):
        if sys.version_info < (3, 0):
            return self.assertRegexpMatches(text, expected_regex)

        return self.assertRegex(text, expected_regex)
