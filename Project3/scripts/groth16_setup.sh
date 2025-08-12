#!/bin/bash

# 安装依赖
npm install -g circom snarkjs

# 1. 编译电路
echo "编译电路中..."
circom circuits/poseidon2.circom --r1cs --wasm -o build

# 2. 下载可信设置文件
echo "下载可信设置..."
wget https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_16.ptau -O build/pot16.ptau

# 3. Groth16 设置
echo "生成Groth16 zKey..."
snarkjs groth16 setup build/poseidon2.r1cs build/pot16.ptau build/circuit.zkey

# 4. 导出验证密钥
echo "导出验证密钥..."
snarkjs zkey export verificationkey build/circuit.zkey build/verification_key.json

# 5. 生成测试输入
echo '{"in": ["12345", "67890"]}' > build/input.json

# 6. 生成证明
echo "生成证明..."
snarkjs groth16 prove build/circuit.zkey build/poseidon2.wasm build/input.json build/proof.json build/public.json

# 7. 验证证明
echo "验证证明..."
snarkjs groth16 verify build/verification_key.json build/public.json build/proof.json

echo "✅ 所有步骤完成！"