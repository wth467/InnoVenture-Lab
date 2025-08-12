pragma circom 2.1.6;

include "constants.circom";

// S-box 模板 (支持全轮和部分轮)
template SBox() {
    signal input in[3];
    signal output out[3];
    
    // 计算 x^5 = (x^2)^2 * x (优化约束)
    signal sq0;
    signal sq1;
    signal sq2;
    signal sq4_0;
    signal sq4_1;
    signal sq4_2;
    
    sq0 <== in[0] * in[0];
    sq1 <== in[1] * in[1];
    sq2 <== in[2] * in[2];
    
    sq4_0 <== sq0 * sq0;
    sq4_1 <== sq1 * sq1;
    sq4_2 <== sq2 * sq2;
    
    out[0] <== sq4_0 * in[0];
    out[1] <== sq4_1 * in[1];
    out[2] <== sq4_2 * in[2];
}

// 部分 S-box 模板 (仅处理第一个元素)
template PartialSBox() {
    signal input in[3];
    signal output out[3];
    
    // 仅对第一个元素计算 x^5
    signal sq0;
    signal sq4_0;
    
    sq0 <== in[0] * in[0];
    sq4_0 <== sq0 * sq0;
    out[0] <== sq4_0 * in[0];
    
    // 其他元素直接输出
    out[1] <== in[1];
    out[2] <== in[2];
}

// MDS 矩阵乘法模板
template MixLayer() {
    signal input in[3];
    signal output out[3];
    
    // MDS 矩阵乘法 (使用预定义矩阵)
    out[0] <== MDS[0][0]*in[0] + MDS[0][1]*in[1] + MDS[0][2]*in[2];
    out[1] <== MDS[1][0]*in[0] + MDS[1][1]*in[1] + MDS[1][2]*in[2];
    out[2] <== MDS[2][0]*in[0] + MDS[2][1]*in[1] + MDS[2][2]*in[2];
}

// Poseidon2 主电路
template Poseidon2() {
    signal input in[2];   // 隐私输入 (原象)
    signal output out;    // 公开输出 (哈希值)
    
    // 状态初始化 [0, in1, in2]
    signal state[3];
    state[0] <== 0;
    state[1] <== in[0];
    state[2] <== in[1];
    
    // 轮常数组件
    component addRC[38];
    
    // S-box 组件
    component sbox[38];
    
    // 混合层组件
    component mix[38];
    
    // 轮函数处理 (总共38轮)
    for (var r = 0; r < 38; r++) {
        // AddRoundConstants
        addRC[r] = AddRoundConstant(r);
        state[0] <== addRC[r].out[0];
        state[1] <== addRC[r].out[1];
        state[2] <== addRC[r].out[2];
        
        // SubWords (S-box)
        if (r < 4 || r >= 34) { // 全轮: 首4轮+尾4轮
            sbox[r] = SBox();
        } else { // 部分轮: 中间30轮
            sbox[r] = PartialSBox();
        }
        sbox[r].in[0] <== state[0];
        sbox[r].in[1] <== state[1];
        sbox[r].in[2] <== state[2];
        
        state[0] <== sbox[r].out[0];
        state[1] <== sbox[r].out[1];
        state[2] <== sbox[r].out[2];
        
        // MixLayer
        mix[r] = MixLayer();
        mix[r].in[0] <== state[0];
        mix[r].in[1] <== state[1];
        mix[r].in[2] <== state[2];
        
        state[0] <== mix[r].out[0];
        state[1] <== mix[r].out[1];
        state[2] <== mix[r].out[2];
    }
    
    // 输出哈希值 (取state[1])
    out <== state[1];
}

// 添加轮常数组件
template AddRoundConstant(round) {
    signal input in[3];
    signal output out[3];
    
    out[0] <== in[0] + RC[round][0];
    out[1] <== in[1] + RC[round][1];
    out[2] <== in[2] + RC[round][2];
}

// 主组件实例化
component main = Poseidon2();