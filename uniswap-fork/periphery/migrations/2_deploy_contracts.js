const Router = artifacts.require("UniswapV2Router02.sol");
const WETH = artifacts.require("WETH.sol");


module.exports = async function (deployer, network) {
  let weth;
  const FACTORY_ADDRESS = '0x242D17a5D4E518a4297DE23008C178d55636F3F4';
  if (network === 'mainnet'){
    weth = await WETH.at('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2');
  } else {
    await deployer.deploy(WETH);
    weth = await WETH.deployed(WETH);
  }
  await deployer.deploy(Router, FACTORY_ADDRESS, weth.address);
};
