const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log(
    "Deploying contracts with the account:",
    deployer.address
  );

  const Greeter = await hre.ethers.getContractFactory("Greeter");
  const greeter = await Greeter.deploy("Hello, World!");

  const Token = await hre.ethers.getContractFactory("SpoonToken");
  const token = await Token.deploy("spoon token ERC20", "spn");

  await greeter.deployed();
  await token.deployed();

  console.log("Greeter deployed to:", greeter.address);
  console.log("Token deployed to:", token.address);
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
