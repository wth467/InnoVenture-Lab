const chai = require("chai");
const wasm_tester = require("circom_tester").wasm;
const path = require("path");

describe("Poseidon2 Hash Test", () => {
  let circuit;
  
  before(async () => {
    circuit = await wasm_tester(
      path.join(__dirname, "../circuits/poseidon2.circom")
    );
  });

  it("正确哈希零输入", async () => {
    const input = { in: ["0", "0"] };
    const witness = await circuit.calculateWitness(input, true);
    await circuit.assertOut(witness, { out: "7853200120776062878684798364095072458815029376092732009249414926327459813530" });
  });

  it("正确哈希随机输入", async () => {
    const input = { 
      in: [
        "12345678901234567890123456789012",
        "98765432109876543210987654321098"
      ] 
    };
    const witness = await circuit.calculateWitness(input, true);
    await circuit.assertOut(witness, { out: "13392975804999668999936548582957313701656901156638557973569667839256315553303" });
  });

  it("验证哈希冲突", async () => {
    const input1 = { in: ["1", "2"] };
    const input2 = { in: ["3", "4"] };
    
    const witness1 = await circuit.calculateWitness(input1, true);
    const witness2 = await circuit.calculateWitness(input2, true);
    
    const out1 = witness1[circuit.getSignalIdx("main.out")].toString();
    const out2 = witness2[circuit.getSignalIdx("main.out")].toString();
    
    chai.expect(out1).to.not.equal(out2);
  });
});