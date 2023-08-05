function dmhelp() {
  echo "dmhelp\t- show usage"
  echo "cigwid\t- comment out igw_id in vpc-id.tf"
  echo "rigwid\t- restore igw_id in vpc-id.tf"
}

function cigwid() {
  for f in aws-*.tf
  do
  if [ -f "${f}.bak" ]; then
      echo "skipped ${f}: .bak aleady exist"
  else
      echo "create ${f}.bak"
      sed -i .bak 's/igw_id/#igw_id/' ${f}
  fi
  done
}

function rigwid() {
  for f in aws-*.bak
  do 
    echo "restore ${f%.bak}"
    mv ${f} ${f%.bak}
  done
}
