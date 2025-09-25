# Post-Quantum Cryptography (PQC)

Post-Quantum Cryptography (PQC) refers to cryptographic algorithms designed to be secure against attacks by quantum computers.

## Motivation
- Shor's algorithm threatens RSA and ECC.
- Grover's algorithm reduces the effective security of symmetric algorithms.
- Migration to PQC is essential before large-scale quantum computers arrive.

## Candidate Families
1. *Lattice-based cryptography*  
   - Uses hard problems in lattices (Learning With Errors).  
   - Examples: Kyber (encryption), Dilithium (signatures).

2. *Hash-based cryptography*  
   - Relies on hash functions for security.  
   - Example: XMSS, SPHINCS+.

3. *Code-based cryptography*  
   - Based on decoding random linear codes.  
   - Example: Classic McEliece.

4. *Multivariate cryptography*  
   - Based on solving multivariate quadratic equations.  
   - Example: Rainbow (though some schemes have been broken).

## Transition Strategies
- *Hybrid encryption*: Combine classical and PQC algorithms during migration.  
- *Standardization*: NIST PQC competition is finalizing standards for deployment.  
- *Long-term security planning*: Organizations should assess cryptographic agility and update systems.

## Challenges
- Larger key sizes compared to classical crypto.  
- Performance overhead in constrained devices.  
- Need for interoperability across systems.