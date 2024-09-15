import random
import string


class RoomKeyGenerator:
    def __init__(self, seed=None):
        """Initialize with an optional seed for reproducibility."""
        if seed is not None:
            random.seed(seed)  # Set the seed for reproducible results

    def generate_key(self, length: int = 6) -> str:
        """Generate a unique random key."""
        characters = string.ascii_letters
        return ''.join(random.choice(characters) for _ in range(length))


# Example usage:
if __name__ == "__main__":
    seed_value = 12345  # Any seed value
    generator_with_seed = RoomKeyGenerator(seed=seed_value)

    print("Generated Room Key with Seed:", generator_with_seed.generate_key())

    # Try generating again with the same seed for identical results
    generator_with_same_seed = RoomKeyGenerator(seed=seed_value)
    print("Generated Room Key with Same Seed:", generator_with_same_seed.generate_key())

    # Generating without a seed for a random key
    generator_without_seed = RoomKeyGenerator()
    print("Generated Room Key without Seed:", generator_without_seed.generate_key())
