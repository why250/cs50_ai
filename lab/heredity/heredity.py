import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def gene_num_probability(ori_gene, offer_gene):
    """
    Compute the probability of a parent with ori_gene genes 
    giving or not giving (depends on the variable offer_gene)
    a mutated gene to his(her) child
    """
    if offer_gene:
        if ori_gene == 0:
            return PROBS["mutation"]
        elif ori_gene == 1:
            return 0.5 # 0.5*(1-Probs["mutation"]) + 0.5*Probs["mutation"] = 0.5
        else :
            return 1 - PROBS["mutation"]
    else:
        if ori_gene == 0:
            return 1 - PROBS["mutation"]
        elif ori_gene == 1:
            return 0.5
        else :
            return PROBS["mutation"]

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    names = people.keys()
    conditions = {
        name:{
            "gene":1 if name in one_gene else 2 if name in two_genes else 0,
            "trait":True if name in have_trait else False
        }for name in names
    }
    p_tot = 1
    for name in names:
        p = 1
        prob_trait_on_condi_gene = PROBS["trait"][conditions[name]["gene"]][conditions[name]["trait"]]
        p *= prob_trait_on_condi_gene
        name_mom = people[name]['mother']
        name_dad = people[name]['father']
        prob_gene = 1
        if name_mom == None or name_dad == None:
            prob_gene *= PROBS['gene'][conditions[name]['gene']]
        else:
            num_gene = conditions[name]['gene']
            if num_gene == 0:
                prob_gene *= gene_num_probability(conditions[name_mom]['gene'],False)
                prob_gene *= gene_num_probability(conditions[name_dad]['gene'],False)
            elif num_gene == 2:
                prob_gene *= gene_num_probability(conditions[name_mom]['gene'],True)
                prob_gene *= gene_num_probability(conditions[name_dad]['gene'],True)
            else:
                p1 = 1
                p1 *= gene_num_probability(conditions[name_mom]['gene'],False)
                p1 *= gene_num_probability(conditions[name_dad]['gene'],True)
                p2 = 1
                p2 *= gene_num_probability(conditions[name_mom]['gene'],True)
                p2 *= gene_num_probability(conditions[name_dad]['gene'],False)
                prob_gene = p1 + p2
        p *= prob_gene
        p_tot *= p
    return p_tot



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    names = probabilities.keys()
    conditions = {
        name:{
            "gene":1 if name in one_gene else 2 if name in two_genes else 0,
            "trait":True if name in have_trait else False
        }for name in names
    }
    for name in names:
        probabilities[name]['gene'][conditions[name]['gene']] += p
        probabilities[name]['trait'][conditions[name]['trait']] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    names = probabilities.keys()
    for name in names:
        normalizer = sum(probabilities[name]['gene'].values())
        for num_gene in probabilities[name]['gene'].keys():
            probabilities[name]['gene'][num_gene] /= normalizer
        normalizer = sum(probabilities[name]['trait'].values())
        for trait in probabilities[name]['trait'].keys():
            probabilities[name]['trait'][trait] /= normalizer

if __name__ == "__main__":
    main()
