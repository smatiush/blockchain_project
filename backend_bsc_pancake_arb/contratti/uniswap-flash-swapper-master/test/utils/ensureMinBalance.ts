import { Signer, BigNumber, Contract } from 'ethers'
import getBalance from './getBalance'
import transfer from './transfer'

export default async function ensureMinBalance(
  contract: Contract,
  tokenSymbol: string,
  minBalance: BigNumber,
  signer: Signer,
  overrides: any
): Promise<void> {
  console.log(`\nEnsuring that contract can cover fees...`)

  let contractTokenPayBalance = await getBalance(tokenSymbol, contract.address, signer)
  console.log(`  contract ${tokenSymbol} balance`, contractTokenPayBalance.toString())

  if (contractTokenPayBalance.lt(minBalance)) {
    console.log(`  contract will not be able to cover fee, sending from signer...`)

    const signerAddress = await signer.getAddress()
    const signerTokenPayBalance = await getBalance(tokenSymbol, signerAddress, signer)
    console.log(`  signer ${tokenSymbol} balance`, signerTokenPayBalance.toString())

    if (signerTokenPayBalance.lt(minBalance)) {
      throw new Error(`Signer does not have ${minBalance.toString()} ${tokenSymbol}`)
    }

    await transfer(contract, tokenSymbol, minBalance, signer, overrides)

    contractTokenPayBalance = await getBalance(tokenSymbol, contract.address, signer)
    console.log(`  new contract ${tokenSymbol} balance`, contractTokenPayBalance.toString())
  }
}

