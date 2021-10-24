import * as assert from 'assert'
import * as addresses from './addresses'
import bre from '@nomiclabs/buidler'
import { Signer, Contract } from 'ethers'
import getDecimals from './utils/getDecimals'
import ensureMinBalance from './utils/ensureMinBalance'

const OVERRIDES = {
  gasLimit: 9.5e6,
  gasPrice: 60e9
}

let signer: Signer
let exampleContract: Contract

function itSuccessfullyFlashSwaps(
  tokenBorrowSymbol: string,
  tokenPaySymbol: string,
  borrowAmount: string,
  feeCushionAmount: string
): void {
  it('successfully flash swaps', async () => {
    console.log(`\nTesting swap - borrows ${borrowAmount} ${tokenBorrowSymbol}, paying with ${tokenPaySymbol}`)

    const amountToBorrow = bre.ethers.utils.parseUnits(borrowAmount, await getDecimals(tokenBorrowSymbol, signer))
    const minBalance = bre.ethers.utils.parseUnits(feeCushionAmount, await getDecimals(tokenPaySymbol, signer))
    await ensureMinBalance(exampleContract, tokenPaySymbol, minBalance, signer, OVERRIDES)

    console.log(`\nPerforming flash swap...`)
    const bytes = bre.ethers.utils.arrayify('0x00')
    await exampleContract.flashSwap(
      addresses.getTokenAddress(tokenBorrowSymbol),
      amountToBorrow,
      addresses.getTokenAddress(tokenPaySymbol),
      bytes
    )

    assert.ok(true)
  })
}

describe('Example', () => {
  before('set up signer', () => {
    console.log('\nSetting up signer...')

    const signerAddress = addresses.getSignerAddress()
    signer = bre.ethers.provider.getSigner(signerAddress)
    console.log(`  signer: ${signerAddress}`)
  })

  before('deploy example contract', async () => {
    console.log('\nDeploying example contract...')
    const factory = await bre.ethers.getContractFactory('ExampleContract', signer)
    exampleContract = await factory.deploy(
      addresses.getTokenAddress('WETH'),
      addresses.getTokenAddress('DAI'),
      OVERRIDES
    )
    console.log(`  example contract: ${exampleContract.address}`)
  })

  // traditional "flash loans" (these incur a 0.3% fee)
  itSuccessfullyFlashSwaps('ETH', 'ETH', '1', '2')
  // itSuccessfullyFlashSwaps('WETH', 'WETH', '1', '2')
  // itSuccessfullyFlashSwaps('DAI', 'DAI', '100', '4')

  // ETH/WETH unwrapping during traditional "flash loans" (these incur a 0.3% fee)
  // itSuccessfullyFlashSwaps('WETH', 'ETH', '1', '2')
  // itSuccessfullyFlashSwaps('ETH', 'WETH', '1', '2')

  // simple flash swaps (these incur a 0.3% fee)
  // itSuccessfullyFlashSwaps('DAI', 'WETH', '100', '0.05')
  // itSuccessfullyFlashSwaps('WETH', 'DAI', '1', '10')

  // ETH/WETH unwrapping with simple flash swaps (these incur a 0.3% fee)
  // itSuccessfullyFlashSwaps('DAI', 'ETH', '100', '0.05')
  // itSuccessfullyFlashSwaps('ETH', 'DAI', '1', '10')

  // triangular swaps (these incur a 0.6% fee)
  // itSuccessfullyFlashSwaps('USDC', 'DAI', '100', '6')
})
