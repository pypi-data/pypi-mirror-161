import torch
from torch.utils.data import Dataset, DataLoader


def get_dataloader(ds, batch_size, shuffle, num_workers=4):  
    return DataLoader(
        ds, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)


class BasicDataset(Dataset):
    def __init__(self, samples):
        '''
        convert array-like <u, i, j> / <u, i, r> / <target_i, context_i, label>

        Parameters
        ----------
        samples : np.array
            samples generated by sampler
        '''        
        super(BasicDataset, self).__init__()
        self.data = samples

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index][0], self.data[index][1], self.data[index][2]

class CandidatesDataset(Dataset):
    def __init__(self, ucands):
        super(CandidatesDataset, self).__init__()
        self.data = ucands

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return torch.tensor(self.data[index][0]), torch.tensor(self.data[index][1])

class AEDataset(Dataset):
    def __init__(self, train_set, yield_col='user'):
        """
        covert user in train_set to array-like <u> / <i> for AutoEncoder-like algorithms
        Parameters
        ----------
        train_set : pd.DataFrame
            training set
        yield_col : string
            column name used to generate array
        """
        super(AEDataset, self).__init__()
        self.data = train_set[yield_col].unique()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]
