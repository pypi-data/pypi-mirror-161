'''
Function:
    Implementation of EMANet
Author:
    Zhenchao Jin
'''
import torch
import torch.nn as nn
import torch.nn.functional as F
from .ema import EMAModule
from ..base import BaseModel
from ...backbones import BuildActivation, BuildNormalization, constructnormcfg


'''EMANet'''
class EMANet(BaseModel):
    def __init__(self, cfg, mode):
        super(EMANet, self).__init__(cfg, mode)
        align_corners, norm_cfg, act_cfg = self.align_corners, self.norm_cfg, self.act_cfg
        # build the EMA module
        ema_cfg = cfg['ema']
        self.ema_in_conv = nn.Sequential(
            nn.Conv2d(ema_cfg['in_channels'], ema_cfg['ema_channels'], kernel_size=3, stride=1, padding=1, bias=False),
            BuildNormalization(constructnormcfg(placeholder=ema_cfg['ema_channels'], norm_cfg=norm_cfg)),
            BuildActivation(act_cfg),
        )
        self.ema_mid_conv = nn.Conv2d(ema_cfg['ema_channels'], ema_cfg['ema_channels'], kernel_size=1, stride=1, padding=0)
        for param in self.ema_mid_conv.parameters():
            param.requires_grad = False
        self.ema_module = EMAModule(
            channels=ema_cfg['ema_channels'],
            num_bases=ema_cfg['num_bases'],
            num_stages=ema_cfg['num_stages'],
            momentum=ema_cfg['momentum']
        )
        self.ema_out_conv = nn.Sequential(
            nn.Conv2d(ema_cfg['ema_channels'], ema_cfg['ema_channels'], kernel_size=1, stride=1, padding=0, bias=False),
            BuildNormalization(constructnormcfg(placeholder=ema_cfg['ema_channels'], norm_cfg=norm_cfg)),
        )
        self.bottleneck = nn.Sequential(
            nn.Conv2d(ema_cfg['ema_channels'], ema_cfg['ema_channels'], kernel_size=3, stride=1, padding=1, bias=False),
            BuildNormalization(constructnormcfg(placeholder=ema_cfg['ema_channels'], norm_cfg=norm_cfg)),
            BuildActivation(act_cfg),
        )
        # build decoder
        decoder_cfg = cfg['decoder']
        self.decoder = nn.Sequential(
            nn.Conv2d(decoder_cfg['in_channels'], decoder_cfg['out_channels'], kernel_size=3, stride=1, padding=1, bias=False),
            BuildNormalization(constructnormcfg(placeholder=decoder_cfg['out_channels'], norm_cfg=norm_cfg)),
            BuildActivation(act_cfg),
            nn.Dropout2d(decoder_cfg['dropout']),
            nn.Conv2d(decoder_cfg['out_channels'], cfg['num_classes'], kernel_size=1, stride=1, padding=0)
        )
        # build auxiliary decoder
        self.setauxiliarydecoder(cfg['auxiliary'])
        # freeze normalization layer if necessary
        if cfg.get('is_freeze_norm', False): self.freezenormalization()
    '''forward'''
    def forward(self, x, targets=None, losses_cfg=None):
        img_size = x.size(2), x.size(3)
        # feed to backbone network
        backbone_outputs = self.transforminputs(self.backbone_net(x), selected_indices=self.cfg['backbone'].get('selected_indices'))
        # feed to EMA module
        feats = self.ema_in_conv(backbone_outputs[-1])
        identity = feats
        feats = self.ema_mid_conv(feats)
        recon = self.ema_module(feats)
        recon = F.relu(recon, inplace=True)
        recon = self.ema_out_conv(recon)
        feats = F.relu(identity + recon, inplace=True)
        feats = self.bottleneck(feats)
        # feed to decoder
        feats = torch.cat([backbone_outputs[-1], feats], dim=1)
        predictions = self.decoder(feats)
        # forward according to the mode
        if self.mode == 'TRAIN':
            loss, losses_log_dict = self.forwardtrain(
                predictions=predictions,
                targets=targets,
                backbone_outputs=backbone_outputs,
                losses_cfg=losses_cfg,
                img_size=img_size,
            )
            return loss, losses_log_dict
        return predictions
    '''return all layers'''
    def alllayers(self):
        all_layers = {
            'backbone_net': self.backbone_net,
            'ema_in_conv': self.ema_in_conv,
            'ema_out_conv': self.ema_out_conv,
            'bottleneck': self.bottleneck,
            'decoder': self.decoder,
        }
        if hasattr(self, 'auxiliary_decoder'):
            all_layers['auxiliary_decoder'] = self.auxiliary_decoder
        return all_layers