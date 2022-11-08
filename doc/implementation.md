# Implementation 
As seen in the `README`, a general language validator in polywit has the following architecture:
<div align="center">
  <img src="images/framework-architecture.png" alt="Polywit Architecture" style="width: 75%;"/><br>
</div>

The package `polywit/base` has the base abstract classes for each component the rest of this document will detail what needs implementing for a new language.

## Validator
The `Validator` is the host for the 3 main components in the diagram. It takes the configuration from the frontend as an argument and this is used to create the 3 components.


## File Processor 
The `FileProcessor` deals with processing of the compilation units. It takes a single constructor parameter for the directory to perform the processing in called `directory`.

This processor needs two functions to be implemented for a language implementation:
- `preprocess` - This is how the files should be processed before having information extracted. This can involve analysing for certain headers or simply moving all files to a temporary directory for compilation.
- `extract_nondet_calls` - This extracts each nondeterministic call in the compilation units and should represent them as a set of position, nondet type pairs.


## Witness Processor
The `WitnessProcessor` deals with processing of the witness. It takes two constructor parameters:
- `directory` - The directory to perform the processing in.
- `witness_path` - The path to the witness.

This processor needs two functions to be implemented for a language:
- `preprocess` - This is how the witness should be processed before extracting any assumptions.
- `extract_assumptions` - This extracts all assumptions from the witness file. This should return an ordered list of assumptions based on their order in the witness.


## Test Harness
The test harness deals with construction and execution of a test to check the validity of the reported violation.

The test harness takes one constructor parameter, `directory` which is the directory where all the processed files from the processors are located.

By default, the test harness has a single defined method:
- `run_test_harness` - This runs the class variable `run_args` which desrcrive how the test harness should be run  as a subprocess.

To implement for a specific language, two functions must be defined:
- `build_test_harness` - This deals with the building and compilation of test harness so it in the state to run. It takes the assumptions as a parameter.
- `_parse_validation_result` - Based on the output of the execution of the program, the output should be parsed and a result field from the `ValidatorResult` enum should be returned.
