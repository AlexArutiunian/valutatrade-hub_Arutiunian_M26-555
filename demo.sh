#!/usr/bin/env bash
set -e

user_name="demo_$(date +%s)"

uv run valuta <<DEMO
register $user_name demo123
login $user_name demo123
show-portfolio
update-rates
show-rates
get-rate USD BTC
buy BTC 0.0001
show-portfolio
sell BTC 0.00002
show-portfolio
buy BTC 999999
exit
DEMO
