# ChallengeAndResponse

This project demonstrates a sample implementation of Challenge and Response Authentication, including key generation, provisioning, and validation processes.

## Prerequisites

- Python 3.10+ installed
- `pip` for Python package management

## Setup and Usage

Follow these steps to set up the environment, generate keys, and perform provisioning and verification tests.

### 1. Setup Python Virtual Environment and Install Dependencies

Run the environment setup script to create a virtual environment and install all required Python packages:

```bash
scripts/local_env_setup.sh
```

This script will:

- Create a Python virtual environment
- Install dependencies specified in the project

### 2. Generate Keys

Use the key generation script to create the necessary keys and data for provisioning:

```bash
scripts/generate_keys.sh
```

This will generate the following data and save it in `output/generated_keys.json`:

- Challenge Key
- Secret
- KEK Seed halves
- Encrypted ipad and opad
- Expected Response

### 3. Write Keys and Start Provisioning Test

Run the provisioning script which will:

- Launch the DUT validation process
- Write keys step-by-step to the DUT simulator
- Perform the provisioning challenge-response verification

```bash
scripts/write_keys_and_start_test.sh
```

The script will output logs indicating each step and whether provisioning succeeded.

## Project Structure

- `src/keys_generator/` — Key generation logic
- `src/keys_validator/` — DUT simulation and provisioning validation
- `scripts/` — Helper shell scripts for setup, key generation, and testing
- `output/` — Generated key files
- `db/` — Persistent context and result JSON files for DUT state

## Notes

- The DUT simulator persists state between commands in `db/provision_context.json`.
- Provisioning results and debug information are saved in `db/provision_result.json`.
- All binary data in JSON files are base64-encoded for compatibility.
- The system uses a custom RC4-based encryption and manual HMAC implementation to simulate the authentication process.

## License

MIT License

---

For detailed technical explanations, refer to the project documentation or contact the maintainer.