import csv
import statistics



import numpy as np



import matplotlib
import matplotlib.pyplot as plt



plt.style.use('seaborn')
plt.rcParams['font.family'] = 'Ubuntu'



def AnalyzeCommunities():
    """
    Analyzes the neuron communities (regions) in the HemiBrain dataset
    """

    neuron_filename = 'CSVs/HemiBrain/traced-neurons.csv'

    neurons = {}

    # open the neuron csv file
    with open(neuron_filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')

        types = set()
        instances = set()

        # skip header
        next(csv_reader, None)
        for row in csv_reader:
            neuron_id = int(row[0])
            type = row[1]
            instance = row[2]

            types.add(type)
            instances.add(instance)

            neurons[neuron_id] = {}
            neurons[neuron_id]['type'] = type
            neurons[neuron_id]['instances'] = type
            neurons[neuron_id]['regions'] = {}

        print ('Neuron Statistics')
        print ('  No. Neurons: {}'.format(len(neurons.keys())))
        print ('  No. Types: {}'.format(len(types)))
        print ('  No. Instancse: {}'.format(len(instances)))

    synapse_filename = 'CSVs/HemiBrain/traced-roi-connections.csv'

    total_synapses_per_region = {}

    with open(synapse_filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')

        nconnections = 0
        nsynapses = 0
        regions = set()

        # skip header
        next(csv_reader, None)
        for row in csv_reader:
            pre_neuron_id = int(row[0])
            post_neuron_id = int(row[1])
            roi = str(row[2])
            weight = int(row[3])

            nconnections += 1
            nsynapses += weight
            regions.add(roi)

            # add weights for this region
            if not roi in neurons[pre_neuron_id]['regions']:
                neurons[pre_neuron_id]['regions'][roi] = weight
            else:
                neurons[pre_neuron_id]['regions'][roi] += weight

            if not roi in neurons[post_neuron_id]['regions']:
                neurons[post_neuron_id]['regions'][roi] = weight
            else:
                neurons[post_neuron_id]['regions'][roi] += weight

            # keep track of the number of synapses per region
            if not roi in total_synapses_per_region:
                total_synapses_per_region[roi] = weight
            else:
                total_synapses_per_region[roi] += weight

        print ('Synapse Statistics')
        print ('  No. Connections: {}'.format(nconnections))
        print ('  No. Synapses: {}'.format(nsynapses))
        print ('  No. Regions: {}'.format(len(regions)))

    synapse_distribution = []
    region_distribution = []
    region_max_weights = []

    # evaluate the regions for each neuron
    for neuron_id in neurons.keys():
        synapses_per_region = neurons[neuron_id]['regions']

        total_synaptic_weight = sum(synapses_per_region.values())

        max_region = None
        max_synaptic_weight = -1

        for region in synapses_per_region.keys():
            if synapses_per_region[region] > max_synaptic_weight:
                max_synaptic_weight = synapses_per_region[region]
                max_region = region

        neurons[neuron_id]['region'] = max_region

        region_weight = max_synaptic_weight / total_synaptic_weight
        no_regions = len(synapses_per_region.keys())

        synapse_distribution.append(total_synaptic_weight)
        region_distribution.append(no_regions)
        region_max_weights.append(region_weight)

    print ()
    print ('Synapses per Neuron')
    print ('  Min: {}'.format(min(synapse_distribution)))
    print ('  Median: {}'.format(statistics.median(synapse_distribution)))
    print ('  Mean: {:0.2f} (+/-{:0.2f})'.format(statistics.mean(synapse_distribution), statistics.stdev(synapse_distribution)))
    print ('  Max: {}'.format(max(synapse_distribution)))

    print ('Regions per Neuron')
    print ('  Min: {}'.format(min(region_distribution)))
    print ('  Median: {}'.format(statistics.median(region_distribution)))
    print ('  Mean: {:0.2f} (+/-{:0.2f})'.format(statistics.mean(region_distribution), statistics.stdev(region_distribution)))
    print ('  Max: {}'.format(max(region_distribution)))

    print ('Region Fidelity')
    print ('  Min: {:0.2f}'.format(min(region_max_weights)))
    print ('  Median: {:0.2f}'.format(statistics.median(region_max_weights)))
    print ('  Mean: {:0.2f} (+/-{:0.2f})'.format(statistics.mean(region_max_weights), statistics.stdev(region_max_weights)))
    print ('  Max: {:0.2f}'.format(max(region_max_weights)))


    # iterate over all neurons and create a synapse confusion matrix
    confusion_matrix = {}

    for neuron_id in neurons.keys():
        neuron_region = neurons[neuron_id]['region']

        # determine the number of synapses in all regions for the neuron
        synapses_per_region = neurons[neuron_id]['regions']
        for region in synapses_per_region.keys():
            # divide by two to avoid double counting for both pre and post synaptic connection
            if not (neuron_region, region) in confusion_matrix:
                confusion_matrix[(neuron_region, region)] = 0.5 * synapses_per_region[region]
            else:
                confusion_matrix[(neuron_region, region)] += 0.5 * synapses_per_region[region]

    # visualize the confusion matrix
    regions = sorted(total_synapses_per_region.items(), key=lambda x : x[1], reverse=True)

    no_regions = len(total_synapses_per_region.keys())
    confusion = np.zeros((no_regions, no_regions), dtype=np.float32)

    region_names = []
    for index_one, (region_one, no_synapses_in_region) in enumerate(regions):
        region_names.append(region_one)
        for index_two, (region_two, _) in enumerate(regions):
            if not (region_one, region_two) in confusion_matrix:
                no_synapses = 0
            else:
                no_synapses = confusion_matrix[(region_one, region_two)]

            confusion[index_one, index_two] = no_synapses / no_synapses_in_region

    fig = plt.figure(figsize=(10, 10), dpi=80)

    ax = fig.add_subplot(111)
    ax.matshow(confusion)

    ax.set_xticks(np.arange(len(region_names)))
    ax.set_xticklabels(region_names, rotation=90)
    ax.set_yticks(np.arange(len(region_names)))
    ax.set_yticklabels(region_names)

    plt.title('Cross-Region Connections', fontsize=28)

    plt.xlabel('Region One', fontsize=22)
    plt.ylabel('Region Two', fontsize=22)

    plt.tight_layout()

    plt.savefig('figures/HemiBrain/cross-region-connections.png')
