import { Signer } from 'ethers'
import getTokenContract from './getTokenContract'

export default async function getDecimals(tokenSymbol: string, signer: Signer): Promise<number> {
  if (tokenSymbol == 'ETH') {
    return 18
  } else {
    const token = await getTokenContract(tokenSymbol, signer)

    return await token.decimals()
  }
}

