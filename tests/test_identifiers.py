from __future__ import annotations

import unittest
import uuid

from jwtgen.domain.identifiers import (
    IdentifierError,
    format_uuid,
    generate_uuid_v4,
    generate_uuid_v4_batch,
)


class TestIdentifiers(unittest.TestCase):
    def test_generate_uuid_v4_has_rfc4122_variant_and_v4(self) -> None:
        value = generate_uuid_v4()
        parsed = uuid.UUID(value)
        self.assertEqual(parsed.version, 4)
        self.assertEqual(parsed.variant, uuid.RFC_4122)

    def test_generate_uuid_v4_batch_count(self) -> None:
        values = generate_uuid_v4_batch(3)
        self.assertEqual(len(values), 3)
        self.assertEqual(len(set(values)), 3)

    def test_generate_uuid_v4_batch_invalid_count(self) -> None:
        with self.assertRaises(IdentifierError):
            generate_uuid_v4_batch(0)

    def test_format_uuid(self) -> None:
        value = "123e4567-e89b-12d3-a456-426614174000"
        self.assertEqual(format_uuid(value, upper=True), value.upper())
        self.assertEqual(format_uuid(value, no_hyphen=True), "123e4567e89b12d3a456426614174000")


if __name__ == "__main__":
    unittest.main()
