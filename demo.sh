#!/usr/bin/env bash
set -e

user_name="demo_$(date +%s)"

uv run valuta <<DEMO
register $user_name demo123
login $user_name demo123
show-portfolio
update-rates
show-rates
get-rate USD EUR
buy EUR 50
show-portfolio
sell EUR 10
show-portfolio
buy EUR 999999
exit
DEMO
