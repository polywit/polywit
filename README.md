<div align="center">
  <img src="https://raw.githubusercontent.com/polywit/polywit/main/images/readme-header.png" alt="Polywit Logo" style="width: 75%;"/><br>
</div>

-----------------

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/14a640b506d146179d1ef26c30cbbeb4)](https://www.codacy.com/gh/polywit/polywit/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=polywit/polywit&amp;utm_campaign=Badge_Grade)

### Description
Modern verification tools report a violation witness amidst verification if a bug is encountered. Polywit employs execution-based validation to check the validity of the counterexample. This process involves extracting information on the assumptions of the verifier from the standardized exchange format for violation witnesses and building a test harness to provide a concrete execution of the program. The tool then executes the test harness on the code under verification and can either confirm or reject the violation witness if the relevant assertion is reached.

Whilst most modern execution-based validators such as wit4java and CPA-wit2test focus on specific language, polywit aims to provide an extensible, feature rich framework to allow for easy language integration and validator quality.

### Terminology
- **position** - A position $p_i$ for a nondeterministic function call from a file $f_i$ and line number the function is called on $n_i$ is represented by the pair $(f_i, n_i)$ .
- **assumption** - An assumption $a_i$ relates the position $p_i$ to the assumed value $v_i$ and is represented as the pair $(p_i, v_i)$.
- **nondet type** - A nondet type for a nondeterministic function call is the return type of the function.
### Literature

- [Wit4Java: A violation-witness validator for Java verifiers (competition contribution)](https://doi.org/10.1007/978-3-030-99527-0_36) by Wu, T., Schrammel, P., & Cordeiro, L. C. International Conference on Tools and Algorithms for the Construction and Analysis of Systems. Springer, Cham, 2022. Springer [doi.org/10.1007/978-3-030-99527-0_36](https://doi.org/10.1007/978-3-030-99527-0_36)
### Usage
```
usage: polywit [-h] frontend ...

Validate a given program with a witness conforming to the appropriate SV-COMP
exchange format.

positional arguments:
  frontend    Frontend language
    java      Use the java validator

options:
  -h, --help  show this help message and exit
```
### Authors
Joss Moffatt (University of Manchester, United Kingdom) josshmoffatt@gmail.com

Tong Wu (University of Manchester, United Kingdom) wutonguom@gmail.com

Lucas Cordeiro (University of Manchester, United Kingdom) lucas.cordeiro@manchester.ac.uk

Peter Schrammel (University of Sussex, United Kingdom) P.Schrammel@sussex.ac.uk
