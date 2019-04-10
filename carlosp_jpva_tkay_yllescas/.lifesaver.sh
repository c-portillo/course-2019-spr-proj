
#!/bin/bash
# Proper header for a Bash script.
for file in *.py
do
  python "$file" >> results.out
done
