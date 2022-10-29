## Terminology
Throughout the program and docs, there exists some polywit-exclusive terminology. The explanation is the following:
- **position** - A position $p_i$ for a nondeterministic function call from a file $f_i$ and line number the function is called on $n_i$ is represented by the pair $(f_i, n_i)$ .
- **assumption** - An assumption $a_i$ relates the position $p_i$ to the assumed value $v_i$ and is represented as the pair $(p_i, v_i)$.
- **nondet type** - A nondet type for a nondeterministic function call is the return type of the function.