require('dotenv').config()
const execa = require('execa')

const validNetworks = ['mainnet', 'rinkeby']

async function main() {
  let network = process.env.NETWORK
  if (!network || validNetworks.indexOf(network) === -1) {
    throw new Error(`Invalid network "${network}" passed on to ./scrits/start-chain.js.\nNetwork must be one of ${validNetworks}`)
  }

  console.log(`NETWORK: ${network}`)
  network = network.toUpperCase()

  const SIGNER_ADDRESS = process.env[`SIGNER_ADDRESS_${network}`]
  if (!SIGNER_ADDRESS) {
    throw new Error('Environment variable SIGNER_ADDRESS must be set. E.g. SIGNER_ADDRESS=0xD3E52099a6a48F132Cb23b1364B7dEE212d862F6')
  }
  console.log(`SIGNER_ADDRESS: ${SIGNER_ADDRESS}`)

  const CHAIN_PROVIDER = process.env[`CHAIN_PROVIDER_${network}`]
  if (!CHAIN_PROVIDER) {
    throw new Error('Environment variable CHAIN_PROVIDER must be set. E.g. CHAIN_PROVIDER=https://mainnet.infura.io/v3/<your_api_key>')
  }
  console.log(`CHAIN_PROVIDER: ${CHAIN_PROVIDER}`)

  execa('npx', [
    'ganache-cli',
    '--fork', CHAIN_PROVIDER,
    '--unlock', SIGNER_ADDRESS,
    '--keepAliveTimeout', '36000000',
    '--networkId', '66',
    '--gasLimit', '10000000'
  ]).stdout.pipe(process.stdout)

  await new Promise(() => {})
}

main()
  .then(console.log)
  .catch(console.error)
