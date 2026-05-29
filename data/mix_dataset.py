import argparse
import pandas as pd

def mix_datasets(source_churn, source_pool, output, total_size, churn_prop, random_state=42):
    df_churn_src = pd.read_csv(source_churn)
    pool = pd.read_csv(source_pool)

    # Pools
    pool_churn = pool[pool['Churn'] == 1]
    pool_unchurn = pool[pool['Churn'] == 0]

    # Combine churn sources
    combined_churn = pd.concat([df_churn_src, pool_churn], ignore_index=True)

    n_churn = int(round(total_size * churn_prop))
    n_unchurn = int(total_size - n_churn)

    replace_churn = n_churn > len(combined_churn)
    replace_unchurn = n_unchurn > len(pool_unchurn)

    sampled_churn = combined_churn.sample(n=n_churn, replace=replace_churn, random_state=random_state)
    sampled_unchurn = pool_unchurn.sample(n=n_unchurn, replace=replace_unchurn, random_state=random_state)

    mixed = pd.concat([sampled_unchurn, sampled_churn], ignore_index=True)
    mixed = mixed.sample(frac=1, random_state=random_state).reset_index(drop=True)
    mixed.to_csv(output, index=False)

    # Print summary
    counts = mixed['Churn'].value_counts().to_dict()
    total = len(mixed)
    print(f"Saved {output} ({total} rows). Churn counts: {counts}")


def main():
    p = argparse.ArgumentParser(description='Mix datasets to given churn proportion')
    p.add_argument('--source-churn', default='data/test.csv')
    p.add_argument('--source-pool', default='data/raw.csv')
    p.add_argument('--output', default='data/test_mixed_70_30.csv')
    p.add_argument('--total-size', type=int, default=None)
    p.add_argument('--churn-prop', type=float, default=0.3)
    args = p.parse_args()

    # Determine default total size
    df_churn_src = pd.read_csv(args.source_churn)
    total_size = args.total_size or len(df_churn_src)

    mix_datasets(args.source_churn, args.source_pool, args.output, total_size, args.churn_prop)


if __name__ == '__main__':
    main()
