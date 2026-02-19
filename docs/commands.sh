#!/usr/bin/env bash

CONFIG="secrets/envs.qa.yaml"
ENV="qa"
PROFILE="admin-service"

echo "==============================="
echo "JWTGEN - UTILIDADES"
echo "==============================="

echo ""
echo "1) Listar ambientes"
jwtgen list-envs -c $CONFIG

echo ""
echo "2) Listar profiles"
jwtgen list-profiles -c $CONFIG -e $ENV

echo ""
echo "3) Mostrar profile"
jwtgen show-profile -c $CONFIG -e $ENV -p $PROFILE

echo ""
echo "4) Generar JWT simple"
jwtgen sign -c $CONFIG -e $ENV -p $PROFILE --sub test

echo ""
echo "5) JWT con TTL personalizado"
jwtgen sign -c $CONFIG -e $ENV -p $PROFILE --sub test --ttl 8h

echo ""
echo "6) JWT con exp absoluto (2030)"
jwtgen sign -c $CONFIG -e $ENV -p $PROFILE --sub test --exp 1893456000

echo ""
echo "7) JWT con claims extra"
jwtgen sign -c $CONFIG -e $ENV -p $PROFILE \
  --sub test \
  --claim scope=admin \
  --claim channel=bruno \
  --print-payload

echo ""
echo "8) JWT con template override"
jwtgen sign -c $CONFIG -e $ENV -p $PROFILE \
  --sub test \
  --payload admin_service \
  --print-payload

echo ""
echo "9) JWT con JSON claim"
jwtgen sign -c $CONFIG -e $ENV -p $PROFILE \
  --sub test \
  --claim meta='{"app":"admin","env":"qa"}' \
  --print-payload