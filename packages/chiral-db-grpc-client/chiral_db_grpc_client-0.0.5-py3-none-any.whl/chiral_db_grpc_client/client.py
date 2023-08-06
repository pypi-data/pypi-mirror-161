import typing
import grpc

from . import chiral_db_pb2
from . import chiral_db_pb2_grpc


class Client:
    def __init__(self, host: str, port: str):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = chiral_db_pb2_grpc.ChiralDbStub(self.channel)

    def __del__(self):
        self.channel.close()

    def get_description(self) -> str:
        return self.stub.GetDescription(chiral_db_pb2.RequestDescription()).desc

    def query_similarity(self, doc_name: str, smiles: str, cutoff: float) -> typing.Dict[str, float]:
        mol = chiral_db_pb2.Molecule(smiles=smiles)
        return self.stub.QuerySimilarity(chiral_db_pb2.RequestSimilarity(mol=mol, cutoff=cutoff, doc_name=doc_name)).results

    def query_substructure(self, doc_name: str, smarts: str) -> typing.Dict[str, chiral_db_pb2.MatchSubstructure]:
        frag = chiral_db_pb2.Fragment(smarts=smarts)
        return self.stub.QuerySubstructure(chiral_db_pb2.RequestSubstructure(doc_name=doc_name, frag=frag)).results

    