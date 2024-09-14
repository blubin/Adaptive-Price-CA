import argparse
import logging
import sys
from adaptiveCA.experiments import experiment, basic, cutting
from adaptiveCA import auctions

logging.basicConfig(level=logging.WARNING, stream=sys.stdout, format='%(message)s')

def main():
    parser = argparse.ArgumentParser(description='Run auction instance.')

    # Define command-line arguments
    parser.add_argument('--print_console', type=bool, default=False, help='Whether to print auction progress to console')
    parser.add_argument('--auction_name', type=str, required=True, help='Name of the auction class')
    parser.add_argument('--generator_param_name', type=str, required=True, help='Generator parameter name')
    parser.add_argument('--epsilon', type=float, default=0.05, help='Auction discount')
    parser.add_argument('--stepc', type=float, default=0.02, help='Step size scaling factor')
    parser.add_argument('--epoch', type=int, default=10, help='Number of epochs')
    parser.add_argument('--personalized', type=bool, default=True, help='Whether to use personalized prices')
    parser.add_argument('--scalebyvalue', type=bool, default=True, help='Whether to scale by value')
    parser.add_argument('--maxiter', type=int, default=1000, help='Maximum number of auction rounds')
    parser.add_argument('--maxtime', type=int, default=120, help='Maximum time in seconds')
    parser.add_argument('--idx', type=int, default=1, help='Instance index')

    args = parser.parse_args()

    if args.auction_name not in [
        "IBundle",
        "LinearClockAuction",
        "LinearSubgradientAuction",
        "LinearHeuristicAuction",
        "AdaptiveCuttingAuction",
    ]:
        raise ValueError("Invalid auction name")

    if args.print_console:
        logging.getLogger().setLevel(logging.INFO)

    auction_class = getattr(auctions, args.auction_name)
    idx = args.idx

    params = {
        'auction_class': auction_class,
        'epsilon': args.epsilon,
        'stepc': args.stepc,
        'epoch': args.epoch,
        'personalized': args.personalized,
        'generator_param_name': args.generator_param_name,
        'scalebyvalue': args.scalebyvalue,
        'maxiter': args.maxiter,
        'maxtime': args.maxtime,
    }

    exp = basic.BasicExperiment()
    exp._param_set_name = 'command_line'
    exp._params = exp._default_param_set()
    exp._params.update(params)

    instance = exp._get_generator_instance(params, idx)
    logging.info(instance)
    auction = exp._get_auction(params, idx, instance)
    auction.run()

if __name__ == '__main__':
    main()
